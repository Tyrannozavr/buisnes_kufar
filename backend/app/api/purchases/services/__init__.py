from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.purchases.repositories import DealRepository
from app.api.purchases.schemas import (
    DealCreate, DealUpdate, DealResponse, BuyerDealResponse, 
    SellerDealResponse, OrderItemResponse, DocumentUpload
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
        try:
            order = await self.repository.create_order(deal_data, buyer_company_id)
            return await self._order_to_deal_response(order)
        except Exception as e:
            await self.session.rollback()
            error_msg = f"Error creating deal: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"Error creating deal: {e}")
            print(traceback.format_exc())
            return None

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
            return None

    async def add_document(self, deal_id: int, document_data: DocumentUpload, file_path: str, company_id: int) -> Optional[OrderDocument]:
        """Добавление документа к сделке"""
        try:
            document_dict = document_data.dict()
            return await self.repository.add_document(deal_id, document_dict, file_path, company_id)
        except Exception as e:
            await self.session.rollback()
            print(f"Error adding document: {e}")
            return None

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
                buyer_company_info = {
                    "id": buyer_company.id,
                    "name": buyer_company.name,
                    "slug": buyer_company.slug,
                    "inn": buyer_company.inn,
                    "phone": buyer_company.phone,
                    "email": buyer_company.email
                }
            
            if seller_company:
                seller_company_info = {
                    "id": seller_company.id,
                    "name": seller_company.name,
                    "slug": seller_company.slug,
                    "inn": seller_company.inn,
                    "phone": seller_company.phone,
                    "email": seller_company.email
                }
            
            print(f"DEBUG: Создаем DealResponse")
            return DealResponse(
                id=order.id,
                buyer_company_id=order.buyer_company_id,
                seller_company_id=order.seller_company_id,
                buyer_order_number=order.buyer_order_number,
                seller_order_number=order.seller_order_number,
                status=order.status,
                deal_type=order.deal_type,
                total_amount=order.total_amount,
                comments=order.comments,
                invoice_number=order.invoice_number,
                contract_number=order.contract_number,
                invoice_date=order.invoice_date,
                contract_date=order.contract_date,
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
                deal_items = []
                for i, item in enumerate(seller_data["items"], 1):
                    deal_items.append({
                        "product_name": item.get("productName"),
                        "product_slug": item.get("slug"),
                        "product_description": item.get("description"),
                        "product_article": str(item.get("article", "")),
                        "product_type": item.get("type"),
                        "logo_url": item.get("logoUrl"),
                        "quantity": item.get("quantity"),
                        "unit_of_measurement": item.get("units"),
                        "price": item.get("price"),
                        "position": i
                    })
                
                deal_data = DealCreate(
                    seller_company_id=seller_id,
                    deal_type=deal_type,
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
