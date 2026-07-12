from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.repositories import DealRepository
from app.api.purchases.schemas import (
	DealCreate,
	DealUpdate,
	DealResponse,
	DealChangeReviewResponse,
	BuyerDealResponse,
	SellerDealResponse,
	OrderItemResponse,
	DocumentUpload,
	CompanyInDealResponse,
	DealStatus,
	DealRole,
	BillInDealResponse,
	SupplyContractInDealResponse,
	CompanyOfficialInDealResponse,
	ContractItem,
	ContractTerms,
	OrderTypeSchema,
)
from app.api.purchases.models import Order, OrderItem, OrderDocument, OrderType
from app.api.company.models.company import Company
from app.api.products.models.product import Product
from app.api.products.repositories.company_products_repository import CompanyProductsRepository
from app_logging.logger import logger


class OnlySellerCanModifyDealError(Exception):
	"""Покупатель не может изменять документы сделки (счёт, договор и т.д.)."""


class BuyerOrderUpdateForbiddenError(Exception):
	"""Покупатель пытается изменить поля, не относящиеся к заказу."""


# Поля DealUpdate, доступные покупателю при редактировании заказа (§3.3)
_BUYER_ORDER_UPDATE_FIELDS = frozenset({
	"status",
	"items",
	"comments",
	"total_amount",
	"amount_vat_rate",
	"amount_with_vat_rate",
	"seller_company",
	"updated_at",
})


class DealChangeReviewForbiddenError(Exception):
	"""Компания не может принять или отклонить эти изменения (не контрагент / инициатор)."""


class DealService:
	"""Сервис для работы с заказами и сделками"""
	
	def __init__(self, session: AsyncSession):
		self.session = session
		self.repository = DealRepository(session)

	async def _ensure_seller_on_deal(self, deal_id: int, company_id: int) -> Optional[Order]:
		"""Доступ к сделке + запрет мутаций документов для компании-покупателя."""
		order = await self.repository.get_order_by_id(deal_id, company_id)
		if not order:
			return None
		if company_id == order.buyer_company_id:
			raise OnlySellerCanModifyDealError()
		return order

	async def _ensure_order_participant(self, deal_id: int, company_id: int) -> Optional[Order]:
		"""Доступ к сделке для покупателя или продавца (редактирование заказа)."""
		return await self.repository.get_order_by_id(deal_id, company_id)

	@staticmethod
	def _filter_update_for_buyer(deal_data: DealUpdate) -> DealUpdate:
		raw = deal_data.model_dump(exclude_none=True)
		forbidden = set(raw) - _BUYER_ORDER_UPDATE_FIELDS
		if forbidden:
			raise BuyerOrderUpdateForbiddenError(
				f"Buyer cannot update deal fields: {', '.join(sorted(forbidden))}"
			)
		return DealUpdate(**raw)

	async def ensure_seller_can_modify_deal(self, deal_id: int, company_id: int) -> Optional[Order]:
		"""Публичная обёртка: доступ к сделке; покупатель → OnlySellerCanModifyDealError."""
		return await self._ensure_seller_on_deal(deal_id, company_id)

	async def create_deal(self, deal_data: DealCreate, buyer_company_id: int) -> Optional[DealResponse]:
		"""Создание новой сделки"""
		from sqlalchemy.exc import IntegrityError
		try:
			order = await self.repository.create_order(deal_data, buyer_company_id)
			return await self._order_to_deal_response(order, buyer_company_id)
		except IntegrityError as e:
			await self.session.rollback()
			logger.exception("Database integrity error creating deal: %s", e)
			# Проверяем, какое ограничение нарушено
			error_str = str(e)
			if "seller_company_id_fkey" in error_str:
				raise ValueError(f"Seller company with ID {deal_data.seller_company_id} does not exist")
			elif "buyer_company_id_fkey" in error_str:
				raise ValueError(f"Buyer company with ID {buyer_company_id} does not exist")
			elif "product_id_fkey" in error_str or "order_items_product_id_fkey" in error_str:
				# Извлекаем product_id из ошибки, если возможно
				import re
				match = re.search(r'Key \(product_id\)=\((\d+)\)', error_str)
				if match:
					product_id = match.group(1)
					raise ValueError(f"Product with ID {product_id} does not exist. Use null or omit product_id for manual entry.")
				raise ValueError("One of the products in the order does not exist. Use null or omit product_id for manual entry.")
			raise ValueError("Database constraint violation")
		except Exception as e:
			await self.session.rollback()
			logger.exception("Error creating deal: %s", e)
			raise

	async def get_order_by_id_only(self, deal_id: int) -> Optional[Order]:
		"""Проверка существования заказа по ID без проверки доступа."""
		return await self.repository.get_order_by_id_only(deal_id)

	async def get_deal_by_id(self, deal_id: int, company_id: int) -> Optional[DealResponse]:
		"""Получение сделки по ID"""
		order = await self.repository.get_order_by_id(deal_id, company_id)
		if not order:
			return None
		return await self._order_to_deal_response(order, company_id)

	async def get_deals_by_ids(self, deal_ids: List[int], company_id: int) -> List[DealResponse]:
		"""Получение сделок по списку ID — пакетная загрузка заказов и владельцев."""
		if not deal_ids:
			return []

		orders = await self.repository.get_orders_by_ids(deal_ids, company_id)
		if not orders:
			return []

		company_ids: set[int] = set()
		for order in orders:
			company_ids.add(order.buyer_company_id)
			company_ids.add(order.seller_company_id)
		owner_names = await self.repository.get_company_owner_names(list(company_ids))

		result: List[DealResponse] = []
		for order in orders:
			deal = await self._order_to_deal_response(
				order, company_id, owner_names=owner_names,
			)
			result.append(deal)
		return result

	async def has_deal_access(self, deal_id: int, company_id: int) -> bool:
		"""Проверка существования сделки и доступа без тяжелой сериализации."""
		order = await self.repository.get_order_by_id(deal_id, company_id)
		return order is not None

	async def get_buyer_deals(self, company_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Order], int]:
		"""Получение заказов покупателя"""
		return await self.repository.get_buyer_orders(company_id, skip, limit)

	async def get_seller_deals(self, company_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Order], int]:
		"""Получение заказов продавца"""
		return await self.repository.get_seller_orders(company_id, skip, limit)

	async def update_deal(self, deal_id: int, deal_data: DealUpdate, company_id: int) -> Optional[DealResponse]:
		"""Обновление сделки"""
		try:
			order = await self._ensure_order_participant(deal_id, company_id)
			if not order:
				return None
			if company_id == order.buyer_company_id:
				deal_data = self._filter_update_for_buyer(deal_data)
			order = await self.repository.update_order(deal_id, deal_data, company_id)
			if not order:
				return None
			return await self._order_to_deal_response(order, company_id)
		except (OnlySellerCanModifyDealError, BuyerOrderUpdateForbiddenError):
			raise
		except Exception as e:
			await self.session.rollback()
			logger.exception("Error updating deal: %s", e)
			raise

	async def create_new_deal_version(
		self, deal_id: int, company_id: int, deal_data: Optional[DealUpdate] = None
	) -> Optional[DealResponse]:
		"""Создание новой версии сделки по текущей последней версии с опциональным обновлением полей."""
		try:
			order = await self._ensure_order_participant(deal_id, company_id)
			if not order:
				return None
			if company_id == order.buyer_company_id and deal_data is not None:
				deal_data = self._filter_update_for_buyer(deal_data)
			order = await self.repository.create_new_order_version(deal_id, company_id)
			if not order:
				return None

			# If request body contains fields, apply them to the newly created latest version.
			# apply_date_fields=True: bill_date, contract_date, supply_contract_date обновляются только здесь
			if deal_data and deal_data.model_dump(exclude_none=True):
				updated_order = await self.repository.update_order(
					deal_id, deal_data, company_id, apply_date_fields=True
				)
				if updated_order:
					order = updated_order

			return await self._order_to_deal_response(order, company_id)
		except (OnlySellerCanModifyDealError, BuyerOrderUpdateForbiddenError):
			raise
		except Exception as e:
			await self.session.rollback()
			logger.exception("Error creating new deal version: %s", e)
			raise

	async def delete_deal(self, deal_id: int, company_id: int) -> bool:
		"""Удаление сделки"""
		try:
			if not await self._ensure_seller_on_deal(deal_id, company_id):
				return False
			deleted = await self.repository.delete_order(deal_id, company_id)
			return deleted
		except OnlySellerCanModifyDealError:
			raise
		except Exception as e:
			await self.session.rollback()
			logger.exception("Error deleting deal: %s", e)
			return False

	async def delete_last_deal_version(self, deal_id: int, company_id: int) -> Optional[int]:
		"""Удаление только последней версии сделки (отклонение контрагентом)."""
		try:
			order = await self.repository.get_order_by_id(deal_id, company_id)
			if not order:
				return None
			if not await self.repository._ensure_counterparty_can_review(order, company_id):
				raise DealChangeReviewForbiddenError()
			return await self.repository.delete_last_order_version(deal_id, company_id)
		except DealChangeReviewForbiddenError:
			raise
		except Exception as e:
			await self.session.rollback()
			logger.exception("Error deleting last deal version: %s", e)
			return None

	async def get_deal_change_review(
		self, deal_id: int, company_id: int
	) -> Optional[DealChangeReviewResponse]:
		state = await self.repository.get_change_review_state(deal_id, company_id)
		if not state:
			return None
		return DealChangeReviewResponse(**state)

	async def accept_deal_changes(self, deal_id: int, company_id: int) -> Optional[DealResponse]:
		try:
			order = await self.repository.accept_order_changes(deal_id, company_id)
			if not order:
				return None
			return await self._order_to_deal_response(order, company_id)
		except Exception as e:
			await self.session.rollback()
			logger.exception("Error accepting deal changes: %s", e)
			return None

	async def reject_deal_changes(self, deal_id: int, company_id: int) -> Optional[int]:
		"""Отклонение изменений — удаление последней версии (только контрагент)."""
		return await self.delete_last_deal_version(deal_id, company_id)

	async def add_document(self, deal_id: int, document_data: DocumentUpload, file_path: str, company_id: int) -> Optional[OrderDocument]:
		"""Добавление документа к сделке"""
		try:
			if not await self._ensure_seller_on_deal(deal_id, company_id):
				return None
			document_dict = document_data.model_dump()
			return await self.repository.add_document(deal_id, document_dict, file_path, company_id)
		except OnlySellerCanModifyDealError:
			raise
		except Exception as e:
			await self.session.rollback()
			logger.exception("Error adding document to deal %s: %s", deal_id, e)
			raise

	async def get_document(self, deal_id: int, document_id: int, company_id: int) -> Optional[OrderDocument]:
		"""Получение документа по ID с проверкой доступа."""
		return await self.repository.get_document_by_id(deal_id, document_id, company_id)

	async def get_documents(self, deal_id: int, company_id: int) -> List[OrderDocument]:
		"""Получение списка документов заказа с проверкой доступа."""
		return await self.repository.get_documents_by_deal_id(deal_id, company_id)

	async def delete_document(self, deal_id: int, document_id: int, company_id: int) -> bool:
		"""Удаление документа из БД (файл из S3 вызывающий код удаляет отдельно)."""
		try:
			if not await self._ensure_seller_on_deal(deal_id, company_id):
				return False
			return await self.repository.delete_document(deal_id, document_id, company_id)
		except OnlySellerCanModifyDealError:
			raise
		except Exception as e:
			logger.exception("Error deleting document from deal %s: %s", deal_id, e)
			raise

	async def assign_bill(self, deal_id: int, company_id: int, date=None):
		"""Генерация и присвоение номера и даты счета."""
		if not await self._ensure_seller_on_deal(deal_id, company_id):
			return None
		return await self.repository.assign_bill(deal_id, company_id, date)

	async def assign_contract(self, deal_id: int, company_id: int, date=None):
		"""Генерация и присвоение номера и даты договора."""
		if not await self._ensure_seller_on_deal(deal_id, company_id):
			return None
		return await self.repository.assign_contract(deal_id, company_id, date)

	async def assign_supply_contract(self, deal_id: int, company_id: int, date=None):
		"""Генерация и присвоение номера и даты договора поставки."""
		if not await self._ensure_seller_on_deal(deal_id, company_id):
			return None
		return await self.repository.assign_supply_contract(deal_id, company_id, date)

	async def get_company_by_user_id(self, user_id: int) -> Optional[Company]:
		"""Получение компании по ID пользователя"""
		return await self.repository.get_company_by_user_id(user_id)

	async def get_units_of_measurement(self) -> List:
		"""Получение единиц измерения"""
		return await self.repository.get_units_of_measurement()

	async def _order_to_deal_response(
		self,
		order: Order,
		company_id: Optional[int] = None,
		owner_names: Optional[dict[int, str]] = None,
	) -> DealResponse:
		"""Преобразование Order в DealResponse с учетом роли компании (buyer/seller)"""
		logger.debug("_order_to_deal_response для заказа %s", order.id)
		
		try:
			# Преобразуем позиции заказа
			logger.debug("Обрабатываем %s позиций заказа", len(order.order_items))
			items = []
			for item in order.order_items:
				# Рассчитываем сумму если она не задана
				amount = item.amount if hasattr(item, 'amount') and item.amount else item.quantity * item.price
				
				items.append(OrderItemResponse(
					id=item.id,
					order_id=order.id,
					product_name=item.product_name,
					product_slug=item.product_slug,
					product_description=item.product_description,
					product_article=item.product_article or "",
					logo_url=item.logo_url,
					quantity=item.quantity,
					unit_of_measurement=item.unit_of_measurement,
					price=item.price,
					amount=amount,
					position=item.position,
					created_at=item.created_at,
					updated_at=item.updated_at
				))
		
			# Информация о компаниях — из eager load или отдельным запросом
			logger.debug("Загружаем компании")
			buyer_company = getattr(order, "buyer_company", None)
			seller_company = getattr(order, "seller_company", None)
			if buyer_company is None:
				logger.debug("Загружаем компанию покупателя %s", order.buyer_company_id)
				buyer_company = await self.repository.get_company_by_id(order.buyer_company_id)
			if seller_company is None:
				logger.debug("Загружаем компанию продавца %s", order.seller_company_id)
				seller_company = await self.repository.get_company_by_id(order.seller_company_id)

			def _owner_name(cid: int) -> str:
				if owner_names and cid in owner_names:
					return owner_names[cid] or ""
				return ""

			buyer_owner_name = (
				_owner_name(order.buyer_company_id)
				if owner_names is not None
				else (await self.repository.get_company_owner_name(order.buyer_company_id) if buyer_company else "")
			)
			seller_owner_name = (
				_owner_name(order.seller_company_id)
				if owner_names is not None
				else (await self.repository.get_company_owner_name(order.seller_company_id) if seller_company else "")
			)

			def _make_company_info(company, owner_name: str, vat_rate_override: Optional[int] = None) -> CompanyInDealResponse:
				return CompanyInDealResponse(
					id=company.id,
					company_name=company.name,
					company_type=company.type,
					full_name=company.full_name or "",
					city=company.city or "",
					name=owner_name or "",
					slug=company.slug or "",
					inn=company.inn,
					ogrn=company.ogrn,
					phone=company.phone or "",
					email=company.email or "",
					legal_address=company.legal_address or "",
					production_address=getattr(company, "production_address", None) or "",
					index=getattr(company, "index", None),
					kpp=company.kpp,
					current_account_number=company.current_account_number,
					correspondent_bank_account=company.correspondent_bank_account,
					bank_name=company.bank_name,
					bic=company.bic,
					vat_rate=vat_rate_override if vat_rate_override is not None else company.vat_rate,
				)

			buyer_company_info = _make_company_info(buyer_company, buyer_owner_name or "") if buyer_company else CompanyInDealResponse(id=0, company_name="", name="", slug="", phone="", email="", legal_address="", production_address="")
			seller_company_info = _make_company_info(seller_company, seller_owner_name or "", getattr(order, "seller_vat_rate", None)) if seller_company else CompanyInDealResponse(id=0, company_name="", name="", slug="", phone="", email="", legal_address="", production_address="")
			
			logger.debug("Создаем DealResponse")
			closing_docs = order.closing_documents if order.closing_documents is not None else []
			others_docs = order.others_documents if order.others_documents is not None else []

			role: Optional[DealRole] = None
			if company_id is not None:
				if company_id == order.buyer_company_id:
					role = DealRole.BUYER
				elif company_id == order.seller_company_id:
					role = DealRole.SELLER

			# bill — объект для фронтенда (number, reason, payment_terms_contract, delivery_terms_contract, additional_info, officials).
			# officials, reason, payment_terms_contract, delivery_terms_contract и additional_info приходят только с клиента при update
			from app.api.purchases.supply_contract_sync import officials_from_json

			officials_list = []
			stored = getattr(order, "bill_officials", None)
			if stored and isinstance(stored, list):
				normalized = []
				for o in stored:
					if isinstance(o, dict):
						item = dict(o)
						item.setdefault("company_id", order.seller_company_id)
						normalized.append(item)
				officials_list = officials_from_json(normalized)
			ct_raw = getattr(order, "contract_terms_contract", None) or ContractTerms.STANDARD_DELIVERY_SUPPLIER.value
			try:
				contract_terms_contract = ContractTerms(ct_raw)
			except ValueError:
				contract_terms_contract = ContractTerms.STANDARD_DELIVERY_SUPPLIER
			cto_raw = getattr(order, "contract_terms_offer", None) or ContractTerms.STANDARD_DELIVERY_SUPPLIER.value
			try:
				contract_terms_offer = ContractTerms(cto_raw)
			except ValueError:
				contract_terms_offer = ContractTerms.STANDARD_DELIVERY_SUPPLIER
			bill_obj = BillInDealResponse(
				number=order.bill_number or "",
				reason=order.bill_reason or "",
				payment_terms=getattr(order, "payment_terms", None) or "",
				payment_terms_contract=order.payment_terms_contract or "",
				delivery_terms_contract=getattr(order, "delivery_terms_contract", None) or "",
				additional_info=order.additional_info or "",
				contract_terms_contract=contract_terms_contract,
				contract_terms_text_contract=getattr(order, "contract_terms_text_contract", None) or "",
				payment_terms_offer=getattr(order, "payment_terms_offer", None) or "",
				contract_terms_offer=contract_terms_offer,
				contract_terms_text_offer=getattr(order, "contract_terms_text_offer", None) or "",
				additional_info_offer=getattr(order, "additional_info_offer", None) or "",
				officials=officials_list,
			)
			from app.api.purchases.supply_contract_sync import build_supply_contract_in_deal_response

			supply_contract_obj = await build_supply_contract_in_deal_response(self.session, order)

			contract_list = []
			if order.contract_number or order.contract_date:
				contract_list.append(
					ContractItem(number=order.contract_number, date=order.contract_date)
				)

			return DealResponse(
				id=order.id,
				version=order.version,
				buyer_company_id=order.buyer_company_id,
				seller_company_id=order.seller_company_id,
				buyer_order_number=order.buyer_order_number,
				seller_order_number=order.seller_order_number,
				deal_type=OrderTypeSchema(order.deal_type.value),
				status=DealStatus(order.status.value),
				total_amount=order.total_amount,
				total_amount_word=getattr(order, "total_amount_word", "") or "",
				total_amount_excl_vat=getattr(order, "total_amount_excl_vat", 0.0),
				amount_vat_rate=getattr(order, "amount_vat_rate", 0.0),
				amount_with_vat_rate=getattr(order, "amount_with_vat_rate", True),
				comments=order.comments or "",
				contract_date=order.contract_date,
				bill_date=order.bill_date,
				supply_contract_date=order.supply_contracts_date,
				closing_documents=closing_docs,
				others_documents=others_docs,
				created_at=order.created_at,
				updated_at=order.updated_at,
				role=role or DealRole.BUYER,
				contract=contract_list,
				bill=bill_obj,
				supply_contract=supply_contract_obj,
				items=items,
				buyer_company=buyer_company_info,
				seller_company=seller_company_info
			)

		except Exception as e:
			logger.exception("Ошибка в _order_to_deal_response для заказа %s: %s (тип: %s)", order.id, e, type(e).__name__)
			raise

	async def _resolve_catalog_product_for_checkout(
		self,
		products_repo: CompanyProductsRepository,
		seller_company_id: int,
		item: dict,
	) -> Optional[Product]:
		"""Каталожная позиция: сначала article, при промахе — slug внутри компании продавца (старые клиенты с Number(article))."""
		raw_art = item.get("article")
		if raw_art is not None and str(raw_art).strip() != "":
			p = await products_repo.get_by_article(str(raw_art).strip())
			if p:
				return p
		slug = item.get("slug")
		if slug and str(slug).strip() and seller_company_id:
			return await products_repo.get_by_company_id_and_slug(
				int(seller_company_id), str(slug).strip()
			)
		return None

	async def _resolve_order_type_for_checkout_item(
		self,
		products_repo: CompanyProductsRepository,
		seller_company_id: int,
		item: dict,
		catalog_product: Optional[Product] = None,
	) -> OrderType:
		"""Тип заказа по productType из корзины или типу позиции в каталоге."""
		raw_type = item.get("productType")
		if raw_type is not None and str(raw_type).strip():
			if str(raw_type).strip() == "Услуга":
				return OrderType.SERVICES
			return OrderType.GOODS

		if catalog_product is None:
			catalog_product = await self._resolve_catalog_product_for_checkout(
				products_repo, seller_company_id, item
			)
		if catalog_product and catalog_product.type:
			from app.api.products.models.product import ProductType

			if catalog_product.type == ProductType.SERVICE:
				return OrderType.SERVICES
		return OrderType.GOODS

	async def _resolve_seller_id_for_checkout_item(
		self,
		products_repo: CompanyProductsRepository,
		item: dict,
	) -> tuple[Optional[int], Optional[Product]]:
		"""Продавец: из companyId в корзине или по slug товара в каталоге."""
		seller_id = item.get("companyId")
		catalog_product: Optional[Product] = None

		slug = item.get("slug")
		if slug and str(slug).strip():
			catalog_product = await products_repo.get_by_slug(str(slug).strip())

		if seller_id is None and catalog_product:
			seller_id = catalog_product.company_id

		if seller_id is None:
			return None, catalog_product

		return int(seller_id), catalog_product

	async def create_deals_from_checkout(
		self, checkout_data: dict, buyer_company_id: int, buyer_user_id: int | None = None
	) -> List[DealResponse]:
		"""Создание заказов из корзины: группировка по продавцу и типу (товары / услуги)."""
		try:
			groups: dict[tuple[int, OrderType], dict] = {}

			for item in checkout_data.get("items", []):
				products_repo = CompanyProductsRepository(self.session)
				seller_id, catalog_product = await self._resolve_seller_id_for_checkout_item(
					products_repo, item
				)
				if seller_id is None:
					logger.warning(
						"Checkout: не удалось определить продавца для позиции slug=%s",
						item.get("slug"),
					)
					continue

				order_type = await self._resolve_order_type_for_checkout_item(
					products_repo, seller_id, item, catalog_product=catalog_product
				)
				key = (seller_id, order_type)
				if key not in groups:
					groups[key] = {
						"seller_company_id": seller_id,
						"order_type": order_type,
						"items": [],
					}
				groups[key]["items"].append(item)

			created_deals: List[DealResponse] = []
			for group in groups.values():
				products_repo = CompanyProductsRepository(self.session)
				seller_id = group["seller_company_id"]
				order_type: OrderType = group["order_type"]

				deal_items = []
				for i, item in enumerate(group["items"], 1):
					catalog_product = await self._resolve_catalog_product_for_checkout(
						products_repo, seller_id, item
					)

					deal_item: dict = {
						"quantity": item.get("quantity"),
						"position": i,
					}

					if catalog_product:
						deal_item["article"] = catalog_product.article
					else:
						pa = item.get("article")
						product_article = (
							str(pa).strip() if pa is not None and str(pa).strip() != "" else ""
						)
						deal_item.update({
							"product_name": item.get("productName"),
							"product_slug": item.get("slug"),
							"product_description": item.get("description"),
							"product_article": product_article,
							"logo_url": item.get("logoUrl"),
							"unit_of_measurement": item.get("units"),
							"price": item.get("price"),
						})

					deal_items.append(deal_item)

				from app.api.purchases.schemas import OrderTypeSchema

				deal_data = DealCreate(
					seller_company_id=seller_id,
					deal_type=OrderTypeSchema(order_type.value),
					items=deal_items,
					comments=checkout_data.get("comments"),
				)

				order = await self.repository.create_order(deal_data, buyer_company_id)
				if buyer_user_id:
					from app.api.purchases.services.checkout_chat_notify import (
						notify_seller_about_checkout_order,
					)

					product_names = [
						str(item.get("productName") or "").strip()
						for item in group["items"]
						if str(item.get("productName") or "").strip()
					]
					await notify_seller_about_checkout_order(
						self.session,
						buyer_company_id=buyer_company_id,
						buyer_user_id=buyer_user_id,
						seller_company_id=seller_id,
						deal_id=order.id,
						seller_order_number=order.seller_order_number,
						order_type=order_type,
						product_names=product_names,
					)
				created_deals.append(
					await self._order_to_deal_response(order, buyer_company_id)
				)

			return created_deals

		except Exception as e:
			await self.session.rollback()
			logger.exception("Error creating deal from checkout: %s", e)
			return []

	async def create_deal_from_checkout(self, checkout_data: dict, buyer_company_id: int) -> Optional[DealResponse]:
		"""Обратная совместимость: первый заказ из checkout."""
		deals = await self.create_deals_from_checkout(checkout_data, buyer_company_id)
		return deals[0] if deals else None
