from typing import Optional, List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, extract
from sqlalchemy.orm import selectinload
from datetime import datetime
import enum

from app.api.purchases.models import Order, OrderItem, OrderHistory, OrderDocument, UnitOfMeasurement, OrderStatus, OrderType
from app.api.purchases.schemas import DealCreate, DealUpdate
from app.api.company.models.company import Company
from app_logging.logger import logger


class DealRepository:
    """Репозиторий для работы с заказами и сделками"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order_data: DealCreate, buyer_company_id: int) -> Order:
        """Создание нового заказа"""
        logger.debug("Начинаем создание заказа для покупателя %s", buyer_company_id)
        
        try:
            # Генерируем номера заказов для покупателя и продавца (ежегодное обнуление)
            logger.debug("Генерируем номер заказа для покупателя %s", buyer_company_id)
            buyer_order_number = await self._generate_order_number(buyer_company_id, "buyer")
            logger.debug("Номер покупателя: %s", buyer_order_number)

            logger.debug("Генерируем номер заказа для продавца %s", order_data.seller_company_id)
            seller_order_number = await self._generate_order_number(order_data.seller_company_id, "seller")
            logger.debug("Номер продавца: %s", seller_order_number)

            order_date = datetime.utcnow()
            
            # Проверяем соответствие типа заказа типам продуктов
            from app.api.purchases.schemas import ItemType
            from app.api.products.models.product import Product, ProductType
            
            # Преобразуем deal_type из ItemType enum в OrderType enum
            if order_data.deal_type == ItemType.GOODS:
                order_deal_type = OrderType.GOODS
                expected_product_type = ProductType.GOOD
            else:
                order_deal_type = OrderType.SERVICES
                expected_product_type = ProductType.SERVICE
            
            # Проверяем все продукты на соответствие типу заказа
            from app.api.products.repositories.company_products_repository import CompanyProductsRepository
            products_repo = CompanyProductsRepository(self.session)
            
            product_types_found = set()
            for item_data in order_data.items:
                if item_data.article:
                    product = await products_repo.get_by_article(item_data.article)
                    if product:
                        product_types_found.add(product.type)
                        # Проверяем соответствие типа продукта типу заказа
                        if product.type != expected_product_type:
                            raise ValueError(
                                f"Product with article '{item_data.article}' is of type '{product.type.value}', "
                                f"but order type is '{order_data.deal_type.value}'. "
                                f"All products must be of type '{expected_product_type.value}' for this order type."
                            )
            
            # Проверяем, что все продукты одного типа (нельзя смешивать товары и услуги)
            if len(product_types_found) > 1:
                types_str = ", ".join([pt.value for pt in product_types_found])
                raise ValueError(
                    f"Cannot mix different product types in one order. Found types: {types_str}. "
                    f"All products in an order must be of the same type (either all goods or all services)."
                )
            
            # Создаем заказ (version starts at 1 for a new deal id)
            logger.debug("Создаем объект Order с типом %s", order_deal_type.value)
            order = Order(
                id=await self._generate_deal_id(),
                version=1,
                buyer_order_number=buyer_order_number,
                seller_order_number=seller_order_number,
                buyer_order_date=order_date,
                seller_order_date=order_date,
                buyer_company_id=buyer_company_id,
                seller_company_id=order_data.seller_company_id,
                deal_type=order_deal_type,
                status=OrderStatus.ACTIVE,
                comments=order_data.comments,
                proposed_by_company_id=None,
                buyer_accepted_at=order_date,
                seller_accepted_at=order_date,
                rejected_by_company_id=None,
            )
            
            logger.debug("Добавляем заказ в сессию")
            self.session.add(order)
            logger.debug("Выполняем flush для получения ID")
            await self.session.flush()  # Получаем ID заказа
            logger.debug("Получен ID заказа: %s", order.id)
            
            # Добавляем позиции заказа
            logger.debug("Добавляем %s позиций заказа", len(order_data.items))
            total_amount = 0
            
            for i, item_data in enumerate(order_data.items, 1):
                position = item_data.position if item_data.position else i
                
                # Если article указан, получаем данные из БД
                product_id = None
                if item_data.article:
                    product = await products_repo.get_by_article(item_data.article)
                    if not product:
                        raise ValueError(f"Product with article '{item_data.article}' not found")
                    
                    product_id = product.id
                    # Используем данные из БД
                    product_name = product.name
                    product_slug = product.slug
                    product_description = product.description
                    product_article = product.article
                    product_type = product.type.value  # Enum -> str
                    logo_url = (product.images[0] if (product.images and len(product.images) > 0) else None)
                    unit_of_measurement = product.unit_of_measurement or "шт"
                    price = product.price if product.price is not None else 0.0
                    quantity = item_data.quantity
                else:
                    # Ручной ввод - используем данные из запроса
                    if not item_data.product_name:
                        raise ValueError("product_name is required when article is not specified")
                    if not item_data.price:
                        raise ValueError("price is required when article is not specified")
                    if not item_data.unit_of_measurement:
                        raise ValueError("unit_of_measurement is required when article is not specified")
                    
                    product_name = item_data.product_name
                    product_slug = item_data.product_slug
                    product_description = item_data.product_description
                    product_article = item_data.product_article
                    product_type = item_data.product_type
                    logo_url = item_data.logo_url
                    unit_of_measurement = item_data.unit_of_measurement
                    price = item_data.price
                    quantity = item_data.quantity
                
                amount = quantity * price
                total_amount += amount

                logger.debug("Обрабатываем позицию %s: %s (qty=%s, price=%s)", position, product_name, quantity, price)
                
                order_item = OrderItem(
                    order_row_id=order.row_id,
                    product_id=product_id,
                    product_name=product_name,
                    product_slug=product_slug,
                    product_description=product_description,
                    product_article=product_article,
                    product_type=product_type,
                    logo_url=logo_url,
                    quantity=quantity,
                    unit_of_measurement=unit_of_measurement,
                    price=price,
                    amount=amount,
                    position=position
                )
                logger.debug("Добавляем позицию в сессию")
                self.session.add(order_item)
            
            order.total_amount = total_amount
            logger.debug("Общая сумма заказа: %s", total_amount)
            
            # Записываем в историю
            logger.debug("Добавляем запись в историю")
            self._add_order_history(
                order.row_id,
                buyer_company_id, 
                "created", 
                "Заказ создан покупателем",
                None,
                order_data.dict()
            )
            
            logger.debug("Выполняем commit")
            await self.session.commit()
            logger.debug("Заказ успешно создан с ID %s", order.id)
            
            # Перезагружаем заказ с связанными данными
            logger.debug("Перезагружаем заказ с связанными данными")
            reloaded_order = await self.get_order_by_id(order.id, buyer_company_id)
            return reloaded_order
            
        except Exception as e:
            logger.exception("Ошибка в create_order: %s (тип: %s)", e, type(e).__name__)
            raise

    async def get_order_by_id_only(self, order_id: int) -> Optional[Order]:
        """Получение latest-версии заказа по ID без проверки доступа (для различения 404/403)."""
        query = (
            select(Order)
            .where(Order.id == order_id)
            .order_by(desc(Order.version))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_order_by_id_and_version(
        self, order_id: int, version: int, company_id: int
    ) -> Optional[Order]:
        """Получение конкретной версии заказа по deal ID и version с проверкой доступа."""
        query = (
            select(Order)
            .options(selectinload(Order.order_items), selectinload(Order.order_history))
            .where(
                and_(
                    Order.id == order_id,
                    Order.version == version,
                    or_(
                        Order.buyer_company_id == company_id,
                        Order.seller_company_id == company_id,
                    ),
                )
            )
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_order_by_id(self, order_id: int, company_id: int) -> Optional[Order]:
        """Получение активной версии заказа (согласованной обеими сторонами, не отклонённой)."""
        return await self.get_active_order(order_id, company_id)

    async def get_latest_order(self, order_id: int, company_id: int) -> Optional[Order]:
        """Получение последней по номеру версии заказа (для редактирования и создания новой версии)."""
        query = (
            select(Order)
            .options(selectinload(Order.order_items), selectinload(Order.order_history))
            .where(
                and_(
                    Order.id == order_id,
                    or_(
                        Order.buyer_company_id == company_id,
                        Order.seller_company_id == company_id,
                    ),
                )
            )
            .order_by(desc(Order.version))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def _active_version_condition(self):
        """Условие: версия не отклонена и принята обеими сторонами (или legacy — без полей согласования)."""
        return and_(
            Order.rejected_by_company_id.is_(None),
            or_(
                and_(
                    Order.buyer_accepted_at.isnot(None),
                    Order.seller_accepted_at.isnot(None),
                ),
                Order.proposed_by_company_id.is_(None),
            ),
        )

    async def get_active_order(self, order_id: int, company_id: int) -> Optional[Order]:
        """Активная версия: последняя по номеру, согласованная обеими сторонами и не отклонённая."""
        query = (
            select(Order)
            .options(selectinload(Order.order_items), selectinload(Order.order_history))
            .where(
                and_(
                    Order.id == order_id,
                    or_(
                        Order.buyer_company_id == company_id,
                        Order.seller_company_id == company_id,
                    ),
                    self._active_version_condition(),
                )
            )
            .order_by(desc(Order.version))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_buyer_orders(self, company_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Order], int]:
        """Получение активных версий заказов покупателя."""
        count_query = select(func.count(func.distinct(Order.id))).where(
            and_(Order.buyer_company_id == company_id, self._active_version_condition())
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        active_subquery = (
            select(Order.id.label("deal_id"), func.max(Order.version).label("max_version"))
            .where(
                and_(
                    Order.buyer_company_id == company_id,
                    self._active_version_condition(),
                )
            )
            .group_by(Order.id)
            .subquery()
        )

        query = (
            select(Order)
            .join(
                active_subquery,
                and_(
                    Order.id == active_subquery.c.deal_id,
                    Order.version == active_subquery.c.max_version,
                ),
            )
            .options(
                selectinload(Order.order_items),
                selectinload(Order.seller_company),
                selectinload(Order.buyer_company),
            )
            .order_by(desc(Order.updated_at))
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        orders = result.scalars().all()

        return list(orders), total

    async def get_seller_orders(self, company_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Order], int]:
        """Получение активных версий заказов продавца."""
        count_query = select(func.count(func.distinct(Order.id))).where(
            and_(Order.seller_company_id == company_id, self._active_version_condition())
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        active_subquery = (
            select(Order.id.label("deal_id"), func.max(Order.version).label("max_version"))
            .where(
                and_(
                    Order.seller_company_id == company_id,
                    self._active_version_condition(),
                )
            )
            .group_by(Order.id)
            .subquery()
        )

        query = (
            select(Order)
            .join(
                active_subquery,
                and_(
                    Order.id == active_subquery.c.deal_id,
                    Order.version == active_subquery.c.max_version,
                ),
            )
            .options(
                selectinload(Order.order_items),
                selectinload(Order.seller_company),
                selectinload(Order.buyer_company),
            )
            .order_by(desc(Order.updated_at))
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        orders = result.scalars().all()

        return list(orders), total

    async def delete_order(self, order_id: int, company_id: int) -> bool:
        """Удаление всех версий заказа."""
        latest_order = await self.get_latest_order(order_id, company_id)
        if not latest_order:
            return False

        query = (
            select(Order)
            .where(
                and_(
                    Order.id == order_id,
                    or_(
                        Order.buyer_company_id == company_id,
                        Order.seller_company_id == company_id,
                    ),
                )
            )
            .order_by(desc(Order.version))
        )
        result = await self.session.execute(query)
        orders = list(result.scalars().all())
        for order in orders:
            await self.session.delete(order)
        await self.session.commit()
        return True

    async def delete_last_order_version(self, order_id: int, company_id: int) -> Optional[int]:
        """Удаление только последней версии заказа. Возвращает удаленную version. Оставлено для совместимости."""
        order = await self.get_latest_order(order_id, company_id)
        if not order:
            return None
        deleted_version = order.version
        await self.session.delete(order)
        await self.session.commit()
        return deleted_version

    async def create_new_order_version(self, order_id: int, company_id: int) -> Optional[Order]:
        """Создание новой версии заказа по последней версии; создатель помечается как предложивший и автоматически принявший."""
        latest_order = await self.get_latest_order(order_id, company_id)
        if not latest_order:
            return None

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        new_version = latest_order.version + 1
        is_buyer = company_id == latest_order.buyer_company_id

        new_order = Order(
            id=latest_order.id,
            version=new_version,
            buyer_order_number=latest_order.buyer_order_number,
            seller_order_number=latest_order.seller_order_number,
            deal_type=latest_order.deal_type,
            status=latest_order.status,
            buyer_company_id=latest_order.buyer_company_id,
            seller_company_id=latest_order.seller_company_id,
            buyer_order_date=self._normalize_datetime(latest_order.buyer_order_date),
            seller_order_date=self._normalize_datetime(latest_order.seller_order_date),
            contract_number=latest_order.contract_number,
            contract_date=self._normalize_datetime(latest_order.contract_date),
            bill_number=latest_order.bill_number,
            bill_date=self._normalize_datetime(latest_order.bill_date),
            supply_contracts_number=latest_order.supply_contracts_number,
            supply_contracts_date=self._normalize_datetime(latest_order.supply_contracts_date),
            closing_documents=latest_order.closing_documents,
            others_documents=latest_order.others_documents,
            comments=latest_order.comments,
            total_amount=latest_order.total_amount,
            proposed_by_company_id=company_id,
            buyer_accepted_at=now if is_buyer else None,
            seller_accepted_at=now if not is_buyer else None,
            rejected_by_company_id=None,
        )

        self.session.add(new_order)
        await self.session.flush()

        for item in latest_order.order_items:
            cloned_item = OrderItem(
                order_row_id=new_order.row_id,
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
                amount=item.amount,
                position=item.position,
            )
            self.session.add(cloned_item)

        self._add_order_history(
            new_order.row_id,
            company_id,
            "version_created",
            f"Создана новая версия сделки: v{new_version}",
            {"source_version": latest_order.version},
            {"version": new_version},
        )

        await self.session.commit()
        return await self.get_order_by_id_and_version(order_id, new_version, company_id)

    async def get_all_versions(self, order_id: int, company_id: int) -> List[Order]:
        """Список всех версий заказа по ID сделки (для выпадающего списка и сравнения)."""
        query = (
            select(Order)
            .options(selectinload(Order.order_items), selectinload(Order.buyer_company), selectinload(Order.seller_company), selectinload(Order.proposed_by_company))
            .where(
                and_(
                    Order.id == order_id,
                    or_(
                        Order.buyer_company_id == company_id,
                        Order.seller_company_id == company_id,
                    ),
                )
            )
            .order_by(desc(Order.version))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def accept_version(self, order_id: int, version: int, company_id: int) -> Optional[Order]:
        """Принять версию (выставить принятие текущей стороной)."""
        order = await self.get_order_by_id_and_version(order_id, version, company_id)
        if not order or order.rejected_by_company_id is not None:
            return None
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if company_id == order.buyer_company_id:
            order.buyer_accepted_at = now
        else:
            order.seller_accepted_at = now
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def reject_version(self, order_id: int, version: int, company_id: int) -> Optional[Order]:
        """Отклонить версию (пометить отклонённой, версия не удаляется)."""
        order = await self.get_order_by_id_and_version(order_id, version, company_id)
        if not order:
            return None
        order.rejected_by_company_id = company_id
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def update_order(self, order_id: int, order_data: DealUpdate, company_id: int) -> Optional[Order]:
        """Обновление заказа (последней версии — та, что редактируется перед «сохранить и отправить»)."""
        order = await self.get_latest_order(order_id, company_id)
        if not order:
            return None
        
        # Сохраняем старые данные для истории
        old_data = {
            "status": order.status,
            "comments": order.comments,
            "contract_number": order.contract_number,
            "bill_number": order.bill_number,
            "bill_date": order.bill_date,
            "supply_contracts_number": order.supply_contracts_number,
            "supply_contracts_date": order.supply_contracts_date,
            "buyer_order_date": order.buyer_order_date,
            "seller_order_date": order.seller_order_date,
        }

        # Обновляем поля
        if order_data.status is not None:
            order.status = order_data.status
        if order_data.comments is not None:
            order.comments = order_data.comments
        if order_data.contract_number is not None:
            order.contract_number = order_data.contract_number
        if order_data.buyer_order_date is not None:
            order.buyer_order_date = order_data.buyer_order_date
        if order_data.seller_order_date is not None:
            order.seller_order_date = order_data.seller_order_date

        # bill_number / bill_date: при установке bill_date без bill_number — генерируем номер
        if order_data.bill_date is not None:
            order.bill_date = order_data.bill_date
            if order_data.bill_number is not None:
                order.bill_number = order_data.bill_number
            elif not order.bill_number:
                order.bill_number = await self._generate_bill_number(order.seller_company_id)
        elif order_data.bill_number is not None:
            order.bill_number = order_data.bill_number

        # supply_contracts_number / supply_contracts_date: при установке date без number — генерируем
        if order_data.supply_contracts_date is not None:
            order.supply_contracts_date = order_data.supply_contracts_date
            if order_data.supply_contracts_number is not None:
                order.supply_contracts_number = order_data.supply_contracts_number
            elif not order.supply_contracts_number:
                order.supply_contracts_number = await self._generate_supply_contract_number(order.seller_company_id)
        elif order_data.supply_contracts_number is not None:
            order.supply_contracts_number = order_data.supply_contracts_number
        
        # Обновляем позиции если нужно
        if order_data.items is not None:
            # Проверяем соответствие типов продуктов типу заказа
            from app.api.products.models.product import Product, ProductType
            from app.api.products.repositories.company_products_repository import CompanyProductsRepository
            products_repo = CompanyProductsRepository(self.session)
            
            # Определяем ожидаемый тип продукта на основе типа заказа
            if order.deal_type == OrderType.GOODS:
                expected_product_type = ProductType.GOOD
            else:
                expected_product_type = ProductType.SERVICE
            
            # Проверяем все продукты на соответствие типу заказа
            product_types_found = set()
            for item_data in order_data.items:
                if item_data.article:
                    product = await products_repo.get_by_article(item_data.article)
                    if product:
                        product_types_found.add(product.type)
                        # Проверяем соответствие типа продукта типу заказа
                        if product.type != expected_product_type:
                            raise ValueError(
                                f"Product with article '{item_data.article}' is of type '{product.type.value}', "
                                f"but order type is '{order.deal_type.value}'. "
                                f"All products must be of type '{expected_product_type.value}' for this order type."
                            )
            
            # Проверяем, что все продукты одного типа (нельзя смешивать товары и услуги)
            if len(product_types_found) > 1:
                types_str = ", ".join([pt.value for pt in product_types_found])
                raise ValueError(
                    f"Cannot mix different product types in one order. Found types: {types_str}. "
                    f"All products in an order must be of the same type (either all goods or all services)."
                )
            
            # Заменяем позиции: очищаем связь (delete-orphan удалит строки в БД), затем добавляем только новые
            order.order_items.clear()
            await self.session.flush()

            total_amount = 0
            for i, item_data in enumerate(order_data.items, 1):
                # Если article указан, получаем данные из БД
                product_id = None
                if item_data.article:
                    product = await products_repo.get_by_article(item_data.article)
                    if not product:
                        raise ValueError(f"Product with article '{item_data.article}' not found")

                    product_id = product.id
                    # Используем данные из БД
                    product_name = product.name
                    product_slug = product.slug
                    product_description = product.description
                    product_article = product.article
                    product_type = product.type.value
                    logo_url = (product.images[0] if (product.images and len(product.images) > 0) else None)
                    unit_of_measurement = product.unit_of_measurement or "шт"
                    price = product.price if product.price is not None else 0.0
                else:
                    # Ручной ввод - используем данные из запроса (price может быть 0 при обновлении)
                    if not item_data.product_name:
                        raise ValueError("product_name is required when article is not specified")
                    if item_data.price is None:
                        raise ValueError("price is required when article is not specified")
                    if not item_data.unit_of_measurement:
                        raise ValueError("unit_of_measurement is required when article is not specified")

                    product_name = item_data.product_name
                    product_slug = item_data.product_slug or None
                    product_description = item_data.product_description or None
                    product_article = item_data.product_article or None
                    product_type = item_data.product_type or None
                    logo_url = item_data.logo_url or None
                    unit_of_measurement = item_data.unit_of_measurement or "шт"
                    price = float(item_data.price)

                amount = item_data.quantity * price
                total_amount += amount

                order_item = OrderItem(
                    order_row_id=order.row_id,
                    product_id=product_id,
                    product_name=product_name,
                    product_slug=product_slug,
                    product_description=product_description,
                    product_article=product_article,
                    product_type=product_type,
                    logo_url=logo_url,
                    quantity=item_data.quantity,
                    unit_of_measurement=unit_of_measurement,
                    price=price,
                    amount=amount,
                    position=i
                )
                order.order_items.append(order_item)

            order.total_amount = total_amount
        
        order.updated_at = datetime.utcnow()
        
        # Записываем в историю
        new_data = {
            "status": order.status,
            "comments": order.comments,
            "contract_number": order.contract_number,
            "bill_number": order.bill_number,
            "bill_date": order.bill_date,
            "supply_contracts_number": order.supply_contracts_number,
            "supply_contracts_date": order.supply_contracts_date,
            "buyer_order_date": order.buyer_order_date,
            "seller_order_date": order.seller_order_date,
        }
        
        self._add_order_history(
            order.row_id,
            company_id,
            "updated",
            "Заказ обновлен",
            old_data,
            new_data
        )
        
        await self.session.commit()
        # Перезагружаем обновлённую последнюю версию (не активную), чтобы вернуть её в ответе
        reloaded = await self.get_latest_order(order_id, company_id)
        return reloaded if reloaded else order

    async def add_document(self, order_id: int, document_data: dict, file_path: str, company_id: int) -> Optional[OrderDocument]:
        """Добавление документа к заказу"""
        order = await self.get_order_by_id(order_id, company_id)
        if not order:
            return None
        
        document = OrderDocument(
            order_row_id=order.row_id,
            document_type=document_data.get("document_type"),
            document_number=(document_data.get("document_number") or "").strip() or "-",
            document_date=document_data.get("document_date") or datetime.utcnow(),
            document_file_path=file_path
        )
        
        self.session.add(document)
        await self.session.commit()

        # Записываем в историю
        self._add_order_history(
            order.row_id,
            company_id,
            "document_added",
            f"Добавлен документ: {document_data.get('document_type', 'Неизвестный тип')}",
            None,
            document_data
        )
        await self.session.commit()

        return document

    async def get_document_by_id(
        self, deal_id: int, document_id: int, company_id: int
    ) -> Optional[OrderDocument]:
        """Получение документа по ID с проверкой доступа к заказу."""
        order = await self.get_order_by_id(deal_id, company_id)
        if not order:
            return None
        query = select(OrderDocument).options(selectinload(OrderDocument.order)).where(
            and_(
                OrderDocument.id == document_id,
                OrderDocument.order_row_id == order.row_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_documents_by_deal_id(
        self, deal_id: int, company_id: int
    ) -> List[OrderDocument]:
        """Получение списка документов заказа с проверкой доступа."""
        order = await self.get_order_by_id(deal_id, company_id)
        if not order:
            return []

        query = (
            select(OrderDocument)
            .options(selectinload(OrderDocument.order))
            .where(OrderDocument.order_row_id == order.row_id)
            .order_by(desc(OrderDocument.created_at))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete_document(
        self, deal_id: int, document_id: int, company_id: int
    ) -> bool:
        """Удаление документа (после удаления файла из S3 вызывающий код должен удалить запись)."""
        doc = await self.get_document_by_id(deal_id, document_id, company_id)
        if not doc:
            return False
        await self.session.delete(doc)
        await self.session.commit()
        return True

    # --- Формы документов (JSON payload): Счет, Договор поставки и т.д., с версионированием ---
    FORM_PLACEHOLDER_NUMBER = "-"

    async def get_document_form(
        self,
        deal_id: int,
        company_id: int,
        document_type: str,
        version: Optional[str] = None,
    ) -> Optional[Tuple[dict, str, Optional[datetime], Optional[int]]]:
        """
        Получение сохранённой формы документа по сделке и типу.
        Возвращает (payload, document_version, updated_at, updated_by_company_id) или None при отсутствии.
        Запись формы: document_number='-', document_file_path IS NULL.
        Если миграция с document_version/updated_by_company_id не применена — используется fallback-запрос без этих колонок.
        """
        order = await self.get_order_by_id(deal_id, company_id)
        if not order:
            return None
        conditions_base = [
            OrderDocument.order_row_id == order.row_id,
            OrderDocument.document_type == document_type,
            OrderDocument.document_number == self.FORM_PLACEHOLDER_NUMBER,
            OrderDocument.document_file_path.is_(None),
        ]
        try:
            conditions = list(conditions_base)
            if version:
                conditions.append(OrderDocument.document_version == version)
            query = (
                select(OrderDocument)
                .where(and_(*conditions))
                .order_by(desc(OrderDocument.updated_at))
            )
            result = await self.session.execute(query)
            doc = result.scalar_one_or_none()
            if not doc:
                return None
            payload = doc.document_content or {}
            doc_version = getattr(doc, "document_version", "v1")
            updated_at = getattr(doc, "updated_at", None)
            updated_by = getattr(doc, "updated_by_company_id", None)
            return (payload, doc_version, updated_at, updated_by)
        except Exception as e:  # noqa: BLE001
            err_msg = str(e).lower()
            if "document_version" in err_msg or "updated_by_company_id" in err_msg or "does not exist" in err_msg:
                logger.warning(
                    "order_documents missing new columns (run migration add_document_form_version_and_updated_by): %s",
                    e,
                )
                return await self._get_document_form_fallback(
                    order.row_id, document_type,
                )
            raise

    async def _get_document_form_fallback(
        self,
        order_row_id: int,
        document_type: str,
    ) -> Optional[Tuple[dict, str, Optional[datetime], Optional[int]]]:
        """Запрос без колонок document_version/updated_by_company_id (до миграции)."""
        conditions = [
            OrderDocument.order_row_id == order_row_id,
            OrderDocument.document_type == document_type,
            OrderDocument.document_number == self.FORM_PLACEHOLDER_NUMBER,
            OrderDocument.document_file_path.is_(None),
        ]
        query = (
            select(OrderDocument.document_content, OrderDocument.updated_at)
            .where(and_(*conditions))
            .order_by(desc(OrderDocument.updated_at))
        )
        result = await self.session.execute(query)
        row = result.one_or_none()
        if not row:
            return None
        payload = row.document_content or {}
        return (payload, "v1", row.updated_at, None)

    async def save_document_form(
        self,
        deal_id: int,
        company_id: int,
        document_type: str,
        payload: dict,
        version: Optional[str] = None,
    ) -> Tuple[dict, str, Optional[datetime], Optional[int]]:
        """
        Сохранение/обновление формы документа. Версионирование: одна запись на (order_row_id, document_type)
        с document_version (по умолчанию v1). При необходимости в будущем можно создавать v1.1, v1.2.
        Возвращает (payload, document_version, updated_at, updated_by_company_id).
        """
        order = await self.get_order_by_id(deal_id, company_id)
        if not order:
            raise ValueError("Deal not found or access denied")
        use_version = version or "v1"
        conditions = [
            OrderDocument.order_row_id == order.row_id,
            OrderDocument.document_type == document_type,
            OrderDocument.document_number == self.FORM_PLACEHOLDER_NUMBER,
            OrderDocument.document_file_path.is_(None),
            OrderDocument.document_version == use_version,
        ]
        query = select(OrderDocument).where(and_(*conditions))
        result = await self.session.execute(query)
        doc = result.scalar_one_or_none()
        now = datetime.utcnow()
        if doc:
            doc.document_content = payload
            doc.updated_at = now
            doc.updated_by_company_id = company_id
            await self.session.commit()
            await self.session.refresh(doc)
            return (
                doc.document_content or {},
                getattr(doc, "document_version", "v1"),
                doc.updated_at,
                getattr(doc, "updated_by_company_id", None),
            )
        doc = OrderDocument(
            order_row_id=order.row_id,
            document_type=document_type,
            document_number=self.FORM_PLACEHOLDER_NUMBER,
            document_date=now,
            document_version=use_version,
            document_content=payload,
            document_file_path=None,
            updated_by_company_id=company_id,
        )
        self.session.add(doc)
        await self.session.commit()
        await self.session.refresh(doc)
        return (
            doc.document_content or {},
            getattr(doc, "document_version", "v1"),
            doc.updated_at,
            getattr(doc, "updated_by_company_id", None),
        )

    async def get_company_by_user_id(self, user_id: int) -> Optional[Company]:
        """Получение компании по ID пользователя"""
        from app.api.authentication.models.user import User
        # Сначала получаем пользователя, затем его компанию
        user_query = select(User).where(User.id == user_id)
        user_result = await self.session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user or not user.company_id:
            return None
        
        # Получаем компанию по company_id из пользователя
        company_query = select(Company).where(Company.id == user.company_id)
        company_result = await self.session.execute(company_query)
        return company_result.scalar_one_or_none()

    async def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """Получение компании по ID"""
        query = select(Company).where(Company.id == company_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_company_owner_name(self, company_id: int) -> Optional[str]:
        """Получение имени владельца компании"""
        from app.api.authentication.models.user import User
        from app.api.authentication.models.roles_positions import UserRole
        
        # Сначала ищем пользователя с ролью OWNER
        owner_query = select(User).where(
            and_(
                User.company_id == company_id,
                User.role == UserRole.OWNER
            )
        ).order_by(User.id.asc()).limit(1)
        
        owner_result = await self.session.execute(owner_query)
        owner = owner_result.scalar_one_or_none()
        
        if owner:
            # Формируем полное имя из first_name, last_name, patronymic
            name_parts = []
            if owner.first_name:
                name_parts.append(owner.first_name)
            if owner.last_name:
                name_parts.append(owner.last_name)
            if owner.patronymic:
                name_parts.append(owner.patronymic)
            
            if name_parts:
                return " ".join(name_parts)
            # Если нет имени, возвращаем email
            return owner.email or ""
        
        # Если нет OWNER, берем первого пользователя компании
        first_user_query = select(User).where(
            User.company_id == company_id
        ).order_by(User.id.asc()).limit(1)
        
        first_user_result = await self.session.execute(first_user_query)
        first_user = first_user_result.scalar_one_or_none()
        
        if first_user:
            name_parts = []
            if first_user.first_name:
                name_parts.append(first_user.first_name)
            if first_user.last_name:
                name_parts.append(first_user.last_name)
            if first_user.patronymic:
                name_parts.append(first_user.patronymic)
            
            if name_parts:
                return " ".join(name_parts)
            return first_user.email or ""
        
        return None

    async def get_units_of_measurement(self) -> List[UnitOfMeasurement]:
        """Получение всех единиц измерения"""
        query = select(UnitOfMeasurement).order_by(UnitOfMeasurement.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _generate_order_number(self, company_id: int, order_type: str) -> str:
        """Генерация номера заказа (маска 00001, ежегодное обнуление).

        order_type: "buyer" — max(buyer_order_number) по buyer_company_id;
                   "seller" — max(seller_order_number) по seller_company_id.
        """
        current_year = datetime.utcnow().year
        if order_type == "buyer":
            col = Order.buyer_order_number
            filter_col = Order.buyer_company_id
        else:
            col = Order.seller_order_number
            filter_col = Order.seller_company_id

        query = select(func.max(col)).where(
            and_(filter_col == company_id, extract("year", Order.created_at) == current_year)
        )
        result = await self.session.execute(query)
        max_number = result.scalar()

        if max_number:
            try:
                number_part = int("".join(filter(str.isdigit, max_number)))
                next_number = number_part + 1
            except (ValueError, AttributeError):
                next_number = 1
        else:
            next_number = 1

        return f"{next_number:05d}"

    async def _generate_deal_id(self) -> int:
        """Генерация нового business deal id (стабильный для всех версий)."""
        query = select(func.max(Order.id))
        result = await self.session.execute(query)
        max_id = result.scalar()
        return (max_id or 0) + 1

    async def _generate_bill_number(self, seller_company_id: int) -> str:
        """Генерация номера счета на оплату (маска 00001, ежегодное обнуление)."""
        current_year = datetime.utcnow().year
        # Используем bill_date если есть, иначе created_at
        date_col = func.coalesce(Order.bill_date, Order.created_at)
        query = (
            select(func.max(Order.bill_number))
            .where(Order.seller_company_id == seller_company_id)
            .where(Order.bill_number.isnot(None))
            .where(extract("year", date_col) == current_year)
        )
        result = await self.session.execute(query)
        max_number = result.scalar()

        if max_number:
            try:
                number_part = int("".join(filter(str.isdigit, max_number)))
                next_number = number_part + 1
            except (ValueError, AttributeError):
                next_number = 1
        else:
            next_number = 1

        return f"{next_number:05d}"

    async def _generate_supply_contract_number(self, seller_company_id: int) -> str:
        """Генерация номера договора поставки (маска 00001, ежегодное обнуление)."""
        current_year = datetime.utcnow().year
        date_col = func.coalesce(Order.supply_contracts_date, Order.created_at)
        query = (
            select(func.max(Order.supply_contracts_number))
            .where(Order.seller_company_id == seller_company_id)
            .where(Order.supply_contracts_number.isnot(None))
            .where(extract("year", date_col) == current_year)
        )
        result = await self.session.execute(query)
        max_number = result.scalar()

        if max_number:
            try:
                number_part = int("".join(filter(str.isdigit, max_number)))
                next_number = number_part + 1
            except (ValueError, AttributeError):
                next_number = 1
        else:
            next_number = 1

        return f"{next_number:05d}"

    async def _generate_contract_number(self, seller_company_id: int) -> str:
        """Генерация номера договора (маска 00001, ежегодное обнуление)."""
        current_year = datetime.utcnow().year
        date_col = func.coalesce(Order.contract_date, Order.created_at)
        query = (
            select(func.max(Order.contract_number))
            .where(Order.seller_company_id == seller_company_id)
            .where(Order.contract_number.isnot(None))
            .where(extract("year", date_col) == current_year)
        )
        result = await self.session.execute(query)
        max_number = result.scalar()

        if max_number:
            try:
                number_part = int("".join(filter(str.isdigit, max_number)))
                next_number = number_part + 1
            except (ValueError, AttributeError):
                next_number = 1
        else:
            next_number = 1

        return f"{next_number:05d}"

    async def assign_bill(self, order_id: int, company_id: int, date: Optional[datetime] = None) -> Optional[Tuple[str, datetime]]:
        """Генерирует и присваивает номер и дату счета заказу. Возвращает (bill_number, bill_date)."""
        order = await self.get_order_by_id(order_id, company_id)
        if not order:
            return None
        bill_date = date or datetime.utcnow()
        if not order.bill_number:
            order.bill_number = await self._generate_bill_number(order.seller_company_id)
        order.bill_date = bill_date
        order.updated_at = datetime.utcnow()
        self._add_order_history(
            order.row_id, company_id, "bill_assigned",
            f"Присвоен счет № {order.bill_number} от {bill_date.strftime('%d.%m.%Y')}",
            None, {"bill_number": order.bill_number, "bill_date": str(bill_date)}
        )
        await self.session.commit()
        return (order.bill_number, order.bill_date)

    async def assign_contract(self, order_id: int, company_id: int, date: Optional[datetime] = None) -> Optional[Tuple[str, datetime]]:
        """Генерирует и присваивает номер и дату договора заказу. Возвращает (contract_number, contract_date)."""
        order = await self.get_order_by_id(order_id, company_id)
        if not order:
            return None
        contract_date = date or datetime.utcnow()
        if not order.contract_number:
            order.contract_number = await self._generate_contract_number(order.seller_company_id)
        order.contract_date = contract_date
        order.updated_at = datetime.utcnow()
        self._add_order_history(
            order.row_id, company_id, "contract_assigned",
            f"Присвоен договор № {order.contract_number} от {contract_date.strftime('%d.%m.%Y')}",
            None, {"contract_number": order.contract_number, "contract_date": str(contract_date)}
        )
        await self.session.commit()
        return (order.contract_number, order.contract_date)

    async def assign_supply_contract(self, order_id: int, company_id: int, date: Optional[datetime] = None) -> Optional[Tuple[str, datetime]]:
        """Генерирует и присваивает номер и дату договора поставки заказу. Возвращает (supply_contracts_number, supply_contracts_date)."""
        order = await self.get_order_by_id(order_id, company_id)
        if not order:
            return None
        supply_date = date or datetime.utcnow()
        if not order.supply_contracts_number:
            order.supply_contracts_number = await self._generate_supply_contract_number(order.seller_company_id)
        order.supply_contracts_date = supply_date
        order.updated_at = datetime.utcnow()
        self._add_order_history(
            order.row_id, company_id, "supply_contract_assigned",
            f"Присвоен договор поставки № {order.supply_contracts_number} от {supply_date.strftime('%d.%m.%Y')}",
            None, {"supply_contracts_number": order.supply_contracts_number, "supply_contracts_date": str(supply_date)}
        )
        await self.session.commit()
        return (order.supply_contracts_number, order.supply_contracts_date)

    @staticmethod
    def _to_json_serializable(obj: Any) -> Any:
        """Приводит значение к виду, сериализуемому в JSON (datetime → строка, enum → value)."""
        if obj is None:
            return None
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, dict):
            return {k: DealRepository._to_json_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [DealRepository._to_json_serializable(v) for v in obj]
        return obj

    @staticmethod
    def _normalize_datetime(value: Optional[datetime]) -> Optional[datetime]:
        """Приводит datetime к naive UTC для полей БД без timezone."""
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.replace(tzinfo=None)

    def _add_order_history(self, order_row_id: int, company_id: int, change_type: str,
                                description: str, old_data: Optional[dict] = None,
                                new_data: Optional[dict] = None):
        """Добавление записи в историю заказа"""
        history = OrderHistory(
            order_row_id=order_row_id,
            changed_by_company_id=company_id,
            change_type=change_type,
            change_description=description,
            old_data=DealRepository._to_json_serializable(old_data),
            new_data=DealRepository._to_json_serializable(new_data)
        )
        self.session.add(history)