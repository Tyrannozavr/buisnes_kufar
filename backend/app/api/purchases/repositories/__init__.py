from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime

from app.api.purchases.models import Order, OrderItem, OrderHistory, OrderDocument, UnitOfMeasurement
from app.api.purchases.schemas import DealStatus, ItemType, OrderItemCreate, DealCreate, DealUpdate
from app.api.company.models.company import Company


class DealRepository:
    """Репозиторий для работы с заказами и сделками"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order_data: DealCreate, buyer_company_id: int) -> Order:
        """Создание нового заказа"""
        # Генерируем номера заказов для покупателя и продавца
        buyer_order_number = await self._generate_order_number(buyer_company_id)
        seller_order_number = await self._generate_order_number(order_data.seller_company_id)
        
        # Создаем заказ
        order = Order(
            buyer_order_number=buyer_order_number,
            seller_order_number=seller_order_number,
            buyer_company_id=buyer_company_id,
            seller_company_id=order_data.seller_company_id,
            deal_type=order_data.deal_type,
            status=DealStatus.ACTIVE,
            comments=order_data.comments
        )
        
        self.session.add(order)
        await self.session.flush()  # Получаем ID заказа
        
        # Добавляем позиции заказа
        total_amount = 0
        for i, item_data in enumerate(order_data.items, 1):
            amount = item_data.quantity * item_data.price
            total_amount += amount
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                product_name=item_data.product_name,
                product_slug=item_data.product_slug,
                product_description=item_data.product_description,
                product_article=item_data.product_article,
                product_type=item_data.product_type,
                logo_url=item_data.logo_url,
                quantity=item_data.quantity,
                unit_of_measurement=item_data.unit_of_measurement,
                price=item_data.price,
                amount=amount,
                position=i
            )
            self.session.add(order_item)
        
        order.total_amount = total_amount
        
        # Записываем в историю
        await self._add_order_history(
            order.id, 
            buyer_company_id, 
            "created", 
            "Заказ создан покупателем",
            None,
            order_data.dict()
        )
        
        await self.session.commit()
        return order

    async def get_order_by_id(self, order_id: int, company_id: int) -> Optional[Order]:
        """Получение заказа по ID с проверкой доступа"""
        query = select(Order).options(
            selectinload(Order.order_items),
            selectinload(Order.buyer_company),
            selectinload(Order.seller_company),
            selectinload(Order.order_history)
        ).where(
            and_(
                Order.id == order_id,
                or_(
                    Order.buyer_company_id == company_id,
                    Order.seller_company_id == company_id
                )
            )
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_buyer_orders(self, company_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Order], int]:
        """Получение заказов покупателя"""
        # Общее количество
        count_query = select(func.count(Order.id)).where(Order.buyer_company_id == company_id)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()
        
        # Заказы
        query = select(Order).options(
            selectinload(Order.order_items),
            selectinload(Order.seller_company)
        ).where(
            Order.buyer_company_id == company_id
        ).order_by(desc(Order.created_at)).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        orders = result.scalars().all()
        
        return list(orders), total

    async def get_seller_orders(self, company_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Order], int]:
        """Получение заказов продавца"""
        # Общее количество
        count_query = select(func.count(Order.id)).where(Order.seller_company_id == company_id)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()
        
        # Заказы
        query = select(Order).options(
            selectinload(Order.order_items),
            selectinload(Order.buyer_company)
        ).where(
            Order.seller_company_id == company_id
        ).order_by(desc(Order.created_at)).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        orders = result.scalars().all()
        
        return list(orders), total

    async def update_order(self, order_id: int, order_data: DealUpdate, company_id: int) -> Optional[Order]:
        """Обновление заказа"""
        order = await self.get_order_by_id(order_id, company_id)
        if not order:
            return None
        
        # Сохраняем старые данные для истории
        old_data = {
            "status": order.status,
            "comments": order.comments,
            "invoice_number": order.invoice_number,
            "contract_number": order.contract_number
        }
        
        # Обновляем поля
        if order_data.status is not None:
            order.status = order_data.status
        if order_data.comments is not None:
            order.comments = order_data.comments
        if order_data.invoice_number is not None:
            order.invoice_number = order_data.invoice_number
        if order_data.contract_number is not None:
            order.contract_number = order_data.contract_number
        
        # Обновляем позиции если нужно
        if order_data.items is not None:
            # Удаляем старые позиции
            await self.session.execute(
                select(OrderItem).where(OrderItem.order_id == order_id)
            )
            old_items = await self.session.execute(
                select(OrderItem).where(OrderItem.order_id == order_id)
            )
            for item in old_items.scalars():
                await self.session.delete(item)
            
            # Добавляем новые позиции
            total_amount = 0
            for i, item_data in enumerate(order_data.items, 1):
                amount = item_data.quantity * item_data.price
                total_amount += amount
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data.product_id,
                    product_name=item_data.product_name,
                    product_slug=item_data.product_slug,
                    product_description=item_data.product_description,
                    product_article=item_data.product_article,
                    product_type=item_data.product_type,
                    logo_url=item_data.logo_url,
                    quantity=item_data.quantity,
                    unit_of_measurement=item_data.unit_of_measurement,
                    price=item_data.price,
                    amount=amount,
                    position=i
                )
                self.session.add(order_item)
            
            order.total_amount = total_amount
        
        order.updated_at = datetime.utcnow()
        
        # Записываем в историю
        new_data = {
            "status": order.status,
            "comments": order.comments,
            "invoice_number": order.invoice_number,
            "contract_number": order.contract_number
        }
        
        await self._add_order_history(
            order.id,
            company_id,
            "updated",
            "Заказ обновлен",
            old_data,
            new_data
        )
        
        await self.session.commit()
        return order

    async def add_document(self, order_id: int, document_data: dict, file_path: str, company_id: int) -> Optional[OrderDocument]:
        """Добавление документа к заказу"""
        order = await self.get_order_by_id(order_id, company_id)
        if not order:
            return None
        
        document = OrderDocument(
            order_id=order_id,
            document_type=document_data.get("document_type"),
            document_number=document_data.get("document_number"),
            document_date=document_data.get("document_date") or datetime.utcnow(),
            document_file_path=file_path
        )
        
        self.session.add(document)
        await self.session.commit()
        
        # Записываем в историю
        await self._add_order_history(
            order_id,
            company_id,
            "document_added",
            f"Добавлен документ: {document_data.get('document_type', 'Неизвестный тип')}",
            None,
            document_data
        )
        
        return document

    async def get_company_by_user_id(self, user_id: int) -> Optional[Company]:
        """Получение компании по ID пользователя"""
        query = select(Company).where(Company.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_units_of_measurement(self) -> List[UnitOfMeasurement]:
        """Получение всех единиц измерения"""
        query = select(UnitOfMeasurement).order_by(UnitOfMeasurement.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _generate_order_number(self, company_id: int) -> str:
        """Генерация номера заказа"""
        # Получаем текущий год
        current_year = datetime.now().year
        
        # Ищем максимальный номер заказа для данной компании в текущем году
        query = select(func.max(Order.buyer_order_number)).where(
            and_(
                Order.buyer_company_id == company_id,
                func.extract('year', Order.created_at) == current_year
            )
        )
        
        result = await self.session.execute(query)
        max_number = result.scalar()
        
        if max_number:
            # Извлекаем числовую часть и увеличиваем на 1
            try:
                number_part = int(max_number.split()[0])
                next_number = number_part + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        # Форматируем номер с ведущими нулями (маска 00000)
        return f"{next_number:05d}"

    async def _add_order_history(self, order_id: int, company_id: int, change_type: str, 
                                description: str, old_data: Optional[dict] = None, 
                                new_data: Optional[dict] = None):
        """Добавление записи в историю заказа"""
        history = OrderHistory(
            order_id=order_id,
            changed_by_company_id=company_id,
            change_type=change_type,
            change_description=description,
            old_data=old_data,
            new_data=new_data
        )
        
        self.session.add(history)