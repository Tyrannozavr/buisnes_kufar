from typing import List, Optional, Union

from pydantic import BaseModel, Field


class CountryCreate(BaseModel):
    """Схема для создания страны"""
    code: str = Field(..., description="ISO код страны (3 символа)", min_length=2, max_length=3)
    name: str = Field(..., description="Название страны", max_length=100)


class FederalDistrictCreate(BaseModel):
    """Схема для создания федерального округа"""
    country_code: str = Field(..., description="ISO код страны", min_length=2, max_length=3)
    name: str = Field(..., description="Название федерального округа", max_length=100)
    code: str = Field(..., description="Код округа (ЦФО, СЗФО и т.д.)", max_length=10)


class RegionCreate(BaseModel):
    """Схема для создания региона"""
    country_code: str = Field(..., description="ISO код страны", min_length=2, max_length=3)
    federal_district_code: Optional[str] = Field(None, description="Код федерального округа")
    name: str = Field(..., description="Название региона", max_length=100)
    code: str = Field(..., description="Код региона", max_length=20)


class CityCreate(BaseModel):
    """Схема для создания города"""
    country_code: str = Field(..., description="ISO код страны", min_length=2, max_length=3)
    region_name: str = Field(..., description="Название региона", max_length=100)
    federal_district_code: Optional[str] = Field(None, description="Код федерального округа")
    name: str = Field(..., description="Название города", max_length=100)
    population: Optional[int] = Field(None, description="Население города", ge=0)
    is_million_city: bool = Field(False, description="Город-миллионник")
    is_regional_center: bool = Field(False, description="Региональный центр")


class LocationCreateResponse(BaseModel):
    """Схема ответа при создании локации"""
    success: bool = Field(..., description="Успешно ли создано")
    message: str = Field(..., description="Сообщение о результате")
    data: Optional[dict] = Field(None, description="Данные созданной локации")


class LocationItem(BaseModel):
    """Базовая модель для элементов локации (страны, регионы, города)"""
    label: str = Field(..., description="Отображаемое название")
    value: str = Field(..., description="Значение для использования в системе")


class CityInfo(BaseModel):
    """Подробная информация о городе"""
    id: int = Field(..., description="Уникальный идентификатор города")
    name: str = Field(..., description="Название города")
    area: Optional[int] = Field(None, description="ID региона")
    telcod: Optional[str] = Field(None, description="Телефонный код")
    latitude: Optional[float] = Field(None, description="Широта")
    longitude: Optional[float] = Field(None, description="Долгота")
    time_zone: Optional[Union[int, str]] = Field(None, description="Часовой пояс")
    english: Optional[str] = Field(None, description="Название на английском")
    rajon: Optional[Union[int, str]] = Field(None, description="ID района")
    country: Optional[str] = Field(None, description="Код страны")
    sound: Optional[str] = Field(None, description="Фонетическое представление")
    level: Optional[Union[int, str]] = Field(None, description="Уровень города (1 - крупнейшие, 2 - крупные)")
    iso: Optional[str] = Field(None, description="ISO код")
    vid: Optional[Union[int, str]] = Field(None, description="Тип населенного пункта")
    full_name: Optional[str] = Field(None, description="Полное название с регионом и районом")


class RegionInfo(BaseModel):
    """Подробная информация о регионе"""
    id: int = Field(..., description="Уникальный идентификатор региона")
    name: str = Field(..., description="Название региона")
    country: str = Field(..., description="Код страны")
    english: Optional[str] = Field(None, description="Название на английском")
    iso: Optional[str] = Field(None, description="ISO код")
    level: Optional[int] = Field(None, description="Уровень региона")


class CountryInfo(BaseModel):
    """Подробная информация о стране"""
    name: str = Field(..., description="Название страны")
    fullname: Optional[str] = Field(None, description="Полное официальное название")
    english: str = Field(..., description="Название на английском")
    id: str = Field(..., description="Код страны")
    country_code3: Optional[str] = Field(None, description="Трехбуквенный код страны")
    iso: Optional[str] = Field(None, description="ISO код")
    telcod: Optional[int] = Field(None, description="Телефонный код")
    location: Optional[str] = Field(None, description="Часть света")
    capital: Optional[int] = Field(None, description="ID столицы")
    mcc: Optional[int] = Field(None, description="Код мобильной связи")
    lang: Optional[str] = Field(None, description="Основной язык")
    langcod: Optional[str] = Field(None, description="Код языка")


class LocationResponse(BaseModel):
    """Модель ответа для списка локаций"""
    items: List[LocationItem] = Field(..., description="Список элементов локации")
    total: int = Field(..., description="Общее количество элементов локации")


class CitySearchResponse(BaseModel):
    """Модель ответа для поиска городов"""
    items: List[CityInfo] = Field(..., description="Список найденных городов")
    total: int = Field(..., description="Общее количество найденных городов")
