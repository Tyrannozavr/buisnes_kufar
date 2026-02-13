from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.repositories import DealRepository
from app.api.purchases.schemas import (
    DealCreate, DealUpdate, DealResponse, BuyerDealResponse,
    SellerDealResponse, OrderItemResponse, DocumentUpload, CompanyInDealResponse,
    DealStatus, ItemType,
)
from app.api.purchases.models import Order, OrderItem, OrderDocument
from app.api.company.models.company import Company


class DealService:
    """Сервис для работы с заказами и сделками"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = DealRepository(session)

    async def create_deal(self, deal_data: DealCreate, buyer_company_id: int) -> Optional[DealResponse]:
        """Создание новой сделки"""
        import traceback
        from app_logging.logger import logger
        from sqlalchemy.exc import IntegrityError
        try:
            order = await self.repository.create_order(deal_data, buyer_company_id)
            return await self._order_to_deal_response(order)
        except IntegrityError as e:
            await self.session.rollback()
            error_msg = f"Database integrity error creating deal: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
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
            error_msg = f"Error creating deal: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"Error creating deal: {e}")
            print(traceback.format_exc())
            raise

    async def get_order_by_id_only(self, deal_id: int) -> Optional[Order]:
        """Проверка существования заказа по ID без проверки доступа."""
        return await self.repository.get_order_by_id_only(deal_id)

    async def get_deal_by_id(self, deal_id: int, company_id: int) -> Optional[DealResponse]:
        """Получение сделки по ID"""
        order = await self.repository.get_order_by_id(deal_id, company_id)
        if not order:
            return None
        return await self._order_to_deal_response(order)

    async def get_buyer_deals(self, company_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Order], int]:
        """Получение заказов покупателя"""
        return await self.repository.get_buyer_orders(company_id, skip, limit)

    async def get_seller_deals(self, company_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Order], int]:
        """Получение заказов продавца"""
        return await self.repository.get_seller_orders(company_id, skip, limit)

    async def update_deal(self, deal_id: int, deal_data: DealUpdate, company_id: int) -> Optional[DealResponse]:
        """Обновление сделки"""
        try:
            order = await self.repository.update_order(deal_id, deal_data, company_id)
            if not order:
                return None
            return await self._order_to_deal_response(order)
        except Exception as e:
            await self.session.rollback()
            print(f"Error updating deal: {e}")
            raise

    async def delete_deal(self, deal_id: int, company_id: int) -> bool:
        """Удаление сделки"""
        try:
            # Проверяем, что сделка существует и пользователь имеет к ней доступ
            order = await self.repository.get_order_by_id(deal_id, company_id)
            if not order:
                return False
            
            # Удаляем сделку
            deleted = await self.repository.delete_order(deal_id, company_id)
            return deleted
        except Exception as e:
            await self.session.rollback()
            print(f"Error deleting deal: {e}")
            return False

    async def add_document(self, deal_id: int, document_data: DocumentUpload, file_path: str, company_id: int) -> Optional[OrderDocument]:
        """Добавление документа к сделке"""
        try:
            document_dict = document_data.dict()
            return await self.repository.add_document(deal_id, document_dict, file_path, company_id)
        except Exception as e:
            await self.session.rollback()
            print(f"Error adding document: {e}")
            return None

    async def assign_bill(self, deal_id: int, company_id: int, date=None):
        """Генерация и присвоение номера и даты счета."""
        return await self.repository.assign_bill(deal_id, company_id, date)

    async def assign_contract(self, deal_id: int, company_id: int, date=None):
        """Генерация и присвоение номера и даты договора."""
        return await self.repository.assign_contract(deal_id, company_id, date)

    async def assign_supply_contract(self, deal_id: int, company_id: int, date=None):
        """Генерация и присвоение номера и даты договора поставки."""
        return await self.repository.assign_supply_contract(deal_id, company_id, date)

    async def get_company_by_user_id(self, user_id: int) -> Optional[Company]:
        """Получение компании по ID пользователя"""
        return await self.repository.get_company_by_user_id(user_id)

    async def get_units_of_measurement(self) -> List:
        """Получение единиц измерения"""
        return await self.repository.get_units_of_measurement()

    async def _order_to_deal_response(self, order: Order) -> DealResponse:
        """Преобразование Order в DealResponse"""
        print(f"DEBUG: _order_to_deal_response для заказа {order.id}")
        
        try:
            # Преобразуем позиции заказа
            print(f"DEBUG: Обрабатываем {len(order.order_items)} позиций заказа")
            items = []
            for item in order.order_items:
                # Рассчитываем сумму если она не задана
                amount = item.amount if hasattr(item, 'amount') and item.amount else item.quantity * item.price
                
                items.append(OrderItemResponse(
                    id=item.id,
                    order_id=item.order_id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    product_slug=item.product_slug,
                    product_description=item.product_description,
                    product_article=item.product_article,
                    product_type=item.product_type,
                    logo_url=item.logo_url,
                    quantity=item.quantity,
                    unit_of_measurement=item.unit_of_measurement,
                    price=item.price,
                    amount=amount,
                    position=item.position,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                ))
        
            # Информация о компаниях - загружаем отдельно
            print(f"DEBUG: Загружаем компании")
            buyer_company_info = None
            seller_company_info = None
            
            # Загружаем компании отдельно
            print(f"DEBUG: Загружаем компанию покупателя {order.buyer_company_id}")
            buyer_company = await self.repository.get_company_by_id(order.buyer_company_id)
            print(f"DEBUG: Загружаем компанию продавца {order.seller_company_id}")
            seller_company = await self.repository.get_company_by_id(order.seller_company_id)
        
            if buyer_company:
                # Получаем имя владельца компании
                buyer_owner_name = await self.repository.get_company_owner_name(order.buyer_company_id)
                buyer_company_info = CompanyInDealResponse(
                    id=buyer_company.id,
                    company_name=buyer_company.name,
                    name=buyer_owner_name or "",
                    slug=buyer_company.slug,
                    inn=buyer_company.inn,
                    phone=buyer_company.phone,
                    email=buyer_company.email,
                    legal_address=buyer_company.legal_address
                )
            
            if seller_company:
                # Получаем имя владельца компании
                seller_owner_name = await self.repository.get_company_owner_name(order.seller_company_id)
                seller_company_info = CompanyInDealResponse(
                    id=seller_company.id,
                    company_name=seller_company.name,
                    name=seller_owner_name or "",
                    slug=seller_company.slug,
                    inn=seller_company.inn,
                    phone=seller_company.phone,
                    email=seller_company.email,
                    legal_address=seller_company.legal_address
                )
            
            print(f"DEBUG: Создаем DealResponse")
            closing_docs = order.closing_documents if order.closing_documents is not None else []
            others_docs = order.others_documents if order.others_documents is not None else []

            return DealResponse(
                id=order.id,
                buyer_company_id=order.buyer_company_id,
                seller_company_id=order.seller_company_id,
                buyer_order_number=order.buyer_order_number,
                seller_order_number=order.seller_order_number,
                status=DealStatus(order.status.value),
                deal_type=ItemType(order.deal_type.value),
                total_amount=order.total_amount,
                comments=order.comments,
                buyer_order_date=order.buyer_order_date,
                seller_order_date=order.seller_order_date,
                contract_number=order.contract_number,
                contract_date=order.contract_date,
                bill_number=order.bill_number,
                bill_date=order.bill_date,
                supply_contracts_number=order.supply_contracts_number,
                supply_contracts_date=order.supply_contracts_date,
                closing_documents=closing_docs,
                others_documents=others_docs,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=items,
                buyer_company=buyer_company_info,
                seller_company=seller_company_info
            )
        
        except Exception as e:
            print(f"DEBUG: Ошибка в _order_to_deal_response: {e}")
            print(f"DEBUG: Тип ошибки: {type(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def create_deal_from_checkout(self, checkout_data: dict, buyer_company_id: int) -> Optional[DealResponse]:
        """Создание заказа из корзины (соответствует фронтенду)"""
        try:
            # Группируем товары по продавцам
            sellers = {}
            for item in checkout_data.get("items", []):
                seller_id = item.get("companyId")
                if seller_id not in sellers:
                    sellers[seller_id] = {
                        "seller_company_id": seller_id,
                        "seller_name": item.get("companyName"),
                        "seller_slug": item.get("companySlug"),
                        "items": []
                    }
                
                sellers[seller_id]["items"].append(item)
            
            # Создаем заказы для каждого продавца
            created_deals = []
            for seller_id, seller_data in sellers.items():
                # Определяем тип заказа (товары или услуги)
                deal_type = "Товары"  # По умолчанию товары
                for item in seller_data["items"]:
                    if item.get("type") == "Услуга":
                        deal_type = "Услуги"
                        break
                
                # Преобразуем данные корзины в формат DealCreate
                # Используем article из корзины для поиска продукта
                from app.api.products.repositories.company_products_repository import CompanyProductsRepository
                products_repo = CompanyProductsRepository(self.session)
                
                deal_items = []
                for i, item in enumerate(seller_data["items"], 1):
                    # Используем article из корзины
                    article = str(item.get("article", "")) if item.get("article") else None
                    
                    deal_item = {
                        "quantity": item.get("quantity"),
                        "position": i
                    }
                    
                    if article:
                        # Если есть article, используем его для поиска продукта
                        deal_item["article"] = article
                    else:
                        # Ручной ввод - все поля обязательны
                        deal_item.update({
                            "product_name": item.get("productName"),
                            "product_slug": item.get("slug"),
                            "product_description": item.get("description"),
                            "product_article": str(item.get("article", "")),
                            "product_type": item.get("type"),
                            "logo_url": item.get("logoUrl"),
                            "unit_of_measurement": item.get("units"),
                            "price": item.get("price")
                        })
                    
                    deal_items.append(deal_item)
                
                # Преобразуем deal_type_str в ItemType enum
                from app.api.purchases.schemas import ItemType
                deal_type_enum = ItemType.GOODS if deal_type == "Товары" else ItemType.SERVICES
                
                deal_data = DealCreate(
                    seller_company_id=seller_id,
                    deal_type=deal_type_enum,
                    items=deal_items,
                    comments=checkout_data.get("comments")
                )
                
                # Создаем заказ
                deal = await self.create_deal(deal_data, buyer_company_id)
                if deal:
                    created_deals.append(deal)
            
            # Возвращаем первый созданный заказ (или можно вернуть список всех)
            return created_deals[0] if created_deals else None
            
        except Exception as e:
            await self.session.rollback()
            print(f"Error creating deal from checkout: {e}")
            return None
