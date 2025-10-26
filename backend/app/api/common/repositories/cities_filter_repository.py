"""
Repository для работы с данными о городах и их фильтрации
"""
from sqlalchemy import select, func, and_
from app.db.base import AsyncSessionLocal
from app.api.common.models.country import Country
from app.api.common.models.federal_district import FederalDistrict
from app.api.common.models.region import Region
from app.api.common.models.city import City
from app.api.company.models.company import Company
from app.api.products.models.product import Product, ProductType


class CitiesFilterRepository:
    """Repository для получения данных о городах с количеством товаров"""
    
    @staticmethod
    async def get_cities_with_products_count():
        """Получить города с количеством товаров через JOIN"""
        async with AsyncSessionLocal() as db:
            # Получаем города с количеством товаров через JOIN
            # Считаем только товары (type=GOOD), исключая услуги
            cities_with_products = await db.execute(
                select(
                    City.id.label('city_id'),
                    City.name.label('city_name'),
                    City.region_id,
                    City.federal_district_id,
                    City.country_id,
                    func.count(Product.id).label('products_count')
                )
                .join(Company, City.id == Company.city_id)
                .join(Product, Company.id == Product.company_id)
                .where(
                    and_(
                        Product.type == ProductType.GOOD,  # Только товары!
                        Product.is_deleted == False,
                        Product.is_hidden == False,
                        City.is_active == True,
                        Company.is_active == True
                    )
                )
                .group_by(
                    City.id,
                    City.name,
                    City.region_id,
                    City.federal_district_id,
                    City.country_id
                )
            )
            
            # Создаем словарь городов с количеством товаров
            cities_data = {}
            for row in cities_with_products:
                cities_data[row.city_id] = {
                    'id': row.city_id,
                    'name': row.city_name,
                    'region_id': row.region_id,
                    'federal_district_id': row.federal_district_id,
                    'country_id': row.country_id,
                    'products_count': row.products_count
                }
            
            print(f"🏙️ Найдено городов с товарами: {len(cities_data)}")
            if cities_data:
                city_example = list(cities_data.values())[0]
                print(f"📊 Пример: {city_example['name']} - {city_example['products_count']} товаров")
            
            return cities_data
    
    @staticmethod
    async def get_regions_by_ids(region_ids):
        """Получить регионы по списку ID"""
        async with AsyncSessionLocal() as db:
            if region_ids:
                result = await db.execute(
                    select(Region)
                    .where(Region.id.in_(region_ids))
                )
                return result.scalars().all()
            return []
    
    @staticmethod
    async def get_federal_districts_by_ids(fd_ids):
        """Получить федеральные округа по списку ID"""
        async with AsyncSessionLocal() as db:
            if fd_ids:
                result = await db.execute(
                    select(FederalDistrict)
                    .where(FederalDistrict.id.in_(fd_ids))
                )
                return result.scalars().all()
            return []
    
    @staticmethod
    async def get_countries_by_ids(country_ids):
        """Получить страны по списку ID"""
        async with AsyncSessionLocal() as db:
            if country_ids:
                result = await db.execute(
                    select(Country)
                    .where(Country.id.in_(country_ids))
                )
                return result.scalars().all()
            return []

