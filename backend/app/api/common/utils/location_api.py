import logging
from typing import Dict, List, Optional, Union

import httpx
from pydantic import BaseModel

from app.core.config import settings
logger = logging.getLogger(__name__)

class LocationAPIError(Exception):
    """Базовый класс для ошибок API локаций"""
    pass


class LocationAPIResponseError(LocationAPIError):
    """Ошибка при получении ответа от API"""
    pass


class LocationAPIConfigError(LocationAPIError):
    """Ошибка конфигурации API"""
    pass


class CityInfo(BaseModel):
    """Информация о городе"""
    id: int
    name: str
    area: Optional[int] = None
    telcod: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    time_zone: Optional[Union[int, str]] = None
    english: Optional[str] = None
    rajon: Optional[Union[int, str]] = None
    country: Optional[str] = None
    sound: Optional[str] = None
    level: Optional[Union[int, str]] = None
    iso: Optional[str] = None
    vid: Optional[Union[int, str]] = None
    full_name: Optional[str] = None


class RegionInfo(BaseModel):
    """Информация о регионе"""
    id: int
    name: str
    country: str
    english: Optional[str] = None
    iso: Optional[str] = None
    level: Optional[int] = None


class CountryInfo(BaseModel):
    """Информация о стране"""
    name: str
    fullname: Optional[str] = None
    english: str
    id: str
    country_code3: Optional[str] = None
    iso: Optional[str] = None
    telcod: Optional[int] = None
    location: Optional[str] = None
    capital: Optional[int] = None
    mcc: Optional[int] = None
    lang: Optional[str] = None
    langcod: Optional[str] = None


class LocationAPI:
    """
    Класс для взаимодействия с внешним API локаций (htmlweb.ru)
    
    Предоставляет методы для получения информации о странах, регионах и городах.
    Все методы возвращают данные в формате, совместимом с фронтендом.
    
    Attributes:
        base_url (str): Базовый URL API
        api_key (str): Ключ API для доступа к сервису
        client (httpx.AsyncClient): HTTP клиент для асинхронных запросов
    """

    def __init__(self):
        """Инициализация клиента API"""
        self.base_url = "http://htmlweb.ru/geo/api.php"
        self.api_key = settings.LOCATION_API_KEY
        logger.error(f"Settings are {settings.__dict__}")
        if not self.api_key:
            logger.error("LOCATION_API_KEY не настроен")
        self.client = httpx.AsyncClient(timeout=10.0)

        # Фиксированный список стран для фронтенда
        self._countries = [
            {"label": "Россия", "value": "RU"},
            {"label": "Беларусь", "value": "BY"},
            {"label": "Казахстан", "value": "KZ"},
            {"label": "Украина", "value": "UA"},
            {"label": "Армения", "value": "AM"},
            {"label": "Азербайджан", "value": "AZ"},
            {"label": "Киргизия", "value": "KG"},
            {"label": "Молдова", "value": "MD"},
            {"label": "Таджикистан", "value": "TJ"},
            {"label": "Узбекистан", "value": "UZ"}
        ]

    async def __aenter__(self):
        """Контекстный менеджер для асинхронного использования"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие клиента при выходе из контекста"""
        await self.client.aclose()

    async def _make_request(self, params: Dict[str, str]) -> Dict:
        """
        Выполняет запрос к API
        
        Args:
            params (Dict[str, str]): Параметры запроса
            
        Returns:
            Dict: Ответ от API
            
        Raises:
            LocationAPIResponseError: При ошибке получения ответа
        """
        try:
            params["json"] = ""
            params["api_key"] = self.api_key
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise LocationAPIResponseError(f"Ошибка при запросе к API: {str(e)}")
        except ValueError as e:
            raise LocationAPIResponseError(f"Ошибка при разборе ответа API: {str(e)}")

    def get_countries(self) -> List[Dict[str, str]]:
        """
        Возвращает фиксированный список стран для фронтенда
        
        Returns:
            List[Dict[str, str]]: Список стран в формате {label: str, value: str}
        """
        return self._countries

    async def get_all_countries(self) -> List[CountryInfo]:
        """
        Получает полный список всех стран из API
        
        Returns:
            List[CountryInfo]: Список стран с полной информацией
        """
        response = await self._make_request({"location": ""})
        return [CountryInfo(**country) for country in response.values() if isinstance(country, dict)]

    async def get_regions(self, country_code: str, area_rajon: int | None = None) -> List[Dict[str, str]]:
        """
        Получает список регионов для указанной страны
        
        Args:
            country_code (str): Код страны (например, 'RU' для России)
            
        Returns:
            List[Dict[str, str]]: Список регионов в формате {label: str, value: str}
        """
        request_data = {"country": country_code.lower()}
        if area_rajon is not None:
            request_data["area_rajon"] = str(area_rajon)
        response = await self._make_request(request_data)

        regions = []
        for region in response.values():
            if isinstance(region, dict) and "id" in region and "name" in region:
                item = {
                    "label": region["name"],
                    "value": str(region["id"]),
                }
                if region.get("okrug"):
                    item["okrug"] = region["okrug"]
                regions.append(item)
        return regions

    async def get_cities(self, region_id: int, level: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Получает список городов для указанного региона
        
        Args:
            region_id (int): ID региона
            level (Optional[int]): Уровень города (1 - крупнейшие, 2 - крупные)
            
        Returns:
            List[Dict[str, str]]: Список городов в формате {label: str, value: str}
        """
        params = {"area": str(region_id)}
        params["perpage"] = 99999

        if level is not None:
            params["level"] = str(level)

        response = await self._make_request(params)
        cities = []
        for city in response.values():
            if isinstance(city, dict) and "id" in city and "name" in city:
                cities.append({
                    "label": city["name"],
                    "value": str(city["id"]),
                })
        return cities

    async def search_cities(self, city_name: str) -> List[CityInfo]:
        """
        Поиск городов по части названия
        
        Args:
            city_name (str): Часть названия города для поиска
            
        Returns:
            List[CityInfo]: Список найденных городов
        """
        response = await self._make_request({"city_name": city_name})
        cities = []
        for city in response.values():
            if isinstance(city, dict) and "id" in city:
                cities.append(CityInfo(**city))
        return cities

    async def get_districts(self, region_id: int) -> List[Dict[str, str]]:
        """
        Получает список районов для указанного региона
        
        Args:
            region_id (int): ID региона
            
        Returns:
            List[Dict[str, str]]: Список районов в формате {label: str, value: str}
        """
        response = await self._make_request({"area_rajon": str(region_id)})
        districts = []
        for district in response.values():
            if isinstance(district, dict) and "id" in district and "name" in district:
                districts.append({
                    "label": district["name"],
                    "value": str(district["id"])
                })
        return districts
