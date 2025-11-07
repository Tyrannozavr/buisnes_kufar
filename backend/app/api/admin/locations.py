from sqladmin import ModelView
from app.api.common.models.country import Country
from app.api.common.models.federal_district import FederalDistrict
from app.api.common.models.region import Region
from app.api.common.models.city import City


class CountryAdmin(ModelView, model=Country):
    name = "Страна"
    name_plural = "Страны"
    icon = "fa-solid fa-globe"
    column_list = [Country.id, Country.code, Country.name, Country.is_active, Country.created_at]
    column_searchable_list = [Country.name, Country.code]
    column_sortable_list = [Country.id, Country.name, Country.created_at]
    column_details_list = [
        Country.id, Country.code, Country.name, 
        Country.is_active, Country.created_at, Country.updated_at
    ]
    form_columns = [Country.code, Country.name, Country.is_active]
    page_size = 50
    page_size_options = [10, 25, 50, 100]


class FederalDistrictAdmin(ModelView, model=FederalDistrict):
    name = "Федеральный округ"
    name_plural = "Федеральные округа"
    icon = "fa-solid fa-map"
    column_list = [
        FederalDistrict.id, FederalDistrict.code, FederalDistrict.name, 
        FederalDistrict.country_id, FederalDistrict.is_active, FederalDistrict.created_at
    ]
    column_searchable_list = [FederalDistrict.name, FederalDistrict.code]
    column_sortable_list = [FederalDistrict.id, FederalDistrict.name, FederalDistrict.country_id]
    column_details_list = [
        FederalDistrict.id, FederalDistrict.code, FederalDistrict.name,
        FederalDistrict.country_id, FederalDistrict.is_active, 
        FederalDistrict.created_at, FederalDistrict.updated_at
    ]
    form_columns = [
        FederalDistrict.code, FederalDistrict.name, 
        FederalDistrict.country_id, FederalDistrict.is_active
    ]
    page_size = 50
    page_size_options = [10, 25, 50, 100]


class RegionAdmin(ModelView, model=Region):
    name = "Регион"
    name_plural = "Регионы"
    icon = "fa-solid fa-building"
    column_list = [
        Region.id, Region.name, Region.code, 
        Region.country_id, Region.federal_district_id, Region.is_active, Region.created_at
    ]
    column_searchable_list = [Region.name, Region.code]
    column_sortable_list = [Region.id, Region.name, Region.country_id, Region.federal_district_id]
    column_details_list = [
        Region.id, Region.name, Region.code,
        Region.country_id, Region.federal_district_id, Region.is_active,
        Region.created_at, Region.updated_at
    ]
    form_columns = [
        Region.name, Region.code, Region.country_id, 
        Region.federal_district_id, Region.is_active
    ]
    page_size = 50
    page_size_options = [10, 25, 50, 100]


class CityAdmin(ModelView, model=City):
    name = "Город"
    name_plural = "Города"
    icon = "fa-solid fa-city"
    column_list = [
        City.id, City.name, City.country_id, City.region_id, City.federal_district_id,
        City.is_active, City.is_million_city, City.is_regional_center, City.created_at
    ]
    column_searchable_list = [City.name]
    column_sortable_list = [
        City.id, City.name, City.country_id, City.region_id, 
        City.federal_district_id, City.is_active
    ]
    column_details_list = [
        City.id, City.name, City.country_id, City.region_id, City.federal_district_id,
        City.is_million_city, City.is_regional_center, City.population,
        City.is_active, City.created_at, City.updated_at
    ]
    form_columns = [
        City.name, City.country_id, City.region_id, City.federal_district_id,
        City.population, City.is_million_city, City.is_regional_center, City.is_active
    ]
    page_size = 50
    page_size_options = [10, 25, 50, 100, 200]

