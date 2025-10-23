from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime

from app.api.purchases.models import Order, OrderItem, OrderHistory, OrderDocument, UnitOfMeasurement, OrderStatus, OrderType
from app.api.purchases.schemas import OrderItemCreate, DealCreate, DealUpdate
from app.api.company.models.company import Company


class DealRepository:
    """Репозиторий для работы с заказами и сделками"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order_data: DealCreate, buyer_company_id: int) -> Order:
        """Создание нового заказа"""
        print(f"DEBUG: Начинаем создание заказа для покупателя {buyer_company_id}")
        
        try:
            # Генерируем номера заказов для покупателя и продавца
            print(f"DEBUG: Генерируем номер заказа для покупателя {buyer_company_id}")
            buyer_order_number = await self._generate_order_number(buyer_company_id)
            print(f"DEBUG: Номер покупателя: {buyer_order_number}")
            
            print(f"DEBUG: Генерируем номер заказа для продавца {order_data.seller_company_id}")
            seller_order_number = await self._generate_order_number(order_data.seller_company_id)
            print(f"DEBUG: Номер продавца: {seller_order_number}")
            
            # Создаем заказ
            print(f"DEBUG: Создаем объект Order")
            order = Order(
                buyer_order_number=buyer_order_number,
                seller_order_number=seller_order_number,
                buyer_company_id=buyer_company_id,
                seller_company_id=order_data.seller_company_id,
                deal_type=OrderType.GOODS if order_data.deal_type == "Товары" else OrderType.SERVICES,
                status=OrderStatus.ACTIVE,
                comments=order_data.comments
            )
            
            print(f"DEBUG: Добавляем заказ в сессию")
            self.session.add(order)
            print(f"DEBUG: Выполняем flush для получения ID")
            await self.session.flush()  # Получаем ID заказа
            print(f"DEBUG: Получен ID заказа: {order.id}")
            
            # Добавляем позиции заказа
            print(f"DEBUG: Добавляем {len(order_data.items)} позиций заказа")
            total_amount = 0
            for i, item_data in enumerate(order_data.items, 1):
                print(f"DEBUG: Обрабатываем позицию {i}: {item_data.product_name}")
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
                print(f"DEBUG: Добавляем позицию в сессию")
                self.session.add(order_item)
            
            order.total_amount = total_amount
            print(f"DEBUG: Общая сумма заказа: {total_amount}")
            
            # Записываем в историю
            print(f"DEBUG: Добавляем запись в историю")
            self._add_order_history(
                order.id, 
                buyer_company_id, 
                "created", 
                "Заказ создан покупателем",
                None,
                order_data.dict()
            )
            
            print(f"DEBUG: Выполняем commit")
            await self.session.commit()
            print(f"DEBUG: Заказ успешно создан с ID {order.id}")
            
            # Перезагружаем заказ с связанными данными
            print(f"DEBUG: Перезагружаем заказ с связанными данными")
            reloaded_order = await self.get_order_by_id(order.id, buyer_company_id)
            return reloaded_order
            
        except Exception as e:
            print(f"DEBUG: Ошибка в create_order: {e}")
            print(f"DEBUG: Тип ошибки: {type(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def get_order_by_id(self, order_id: int, company_id: int) -> Optional[Order]:
        """Получение заказа по ID с проверкой доступа"""
        query = select(Order).options(
            selectinload(Order.order_items),
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
            selectinload(Order.order_items)
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
            selectinload(Order.order_items)
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
                self.session.delete(item)
            
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
        
        self._add_order_history(
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
        self._add_order_history(
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

    async def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """Получение компании по ID"""
        query = select(Company).where(Company.id == company_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_units_of_measurement(self) -> List[UnitOfMeasurement]:
        """Получение всех единиц измерения"""
        query = select(UnitOfMeasurement).order_by(UnitOfMeasurement.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _generate_order_number(self, company_id: int) -> str:
        """Генерация номера заказа"""
        print(f"DEBUG: _generate_order_number для компании {company_id}")
        
        try:
            # Ищем максимальный номер заказа для данной компании
            print(f"DEBUG: Выполняем запрос для поиска максимального номера")
            query = select(func.max(Order.buyer_order_number)).where(
                Order.buyer_company_id == company_id
            )
            
            print(f"DEBUG: Выполняем execute запроса")
            result = await self.session.execute(query)
            print(f"DEBUG: Получаем scalar результат")
            max_number = result.scalar()
            print(f"DEBUG: Максимальный номер: {max_number}")
            
            if max_number:
                # Извлекаем числовую часть и увеличиваем на 1
                try:
                    # Убираем все нецифровые символы и преобразуем в int
                    number_part = int(''.join(filter(str.isdigit, max_number)))
                    next_number = number_part + 1
                    print(f"DEBUG: Следующий номер: {next_number}")
                except (ValueError, AttributeError):
                    next_number = 1
                    print(f"DEBUG: Ошибка парсинга, используем номер 1")
            else:
                next_number = 1
                print(f"DEBUG: Нет существующих номеров, начинаем с 1")
            
            # Форматируем номер с ведущими нулями (маска 00000)
            formatted_number = f"{next_number:05d}"
            print(f"DEBUG: Отформатированный номер: {formatted_number}")
            return formatted_number
            
        except Exception as e:
            print(f"DEBUG: Ошибка в _generate_order_number: {e}")
            print(f"DEBUG: Тип ошибки: {type(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _add_order_history(self, order_id: int, company_id: int, change_type: str, 
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