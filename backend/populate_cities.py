#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных городами России
Адаптирует данные из complete_cities_db_final.sql под PostgreSQL
"""

import asyncio
import asyncpg
import os
from typing import List, Dict, Any
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Данные для заполнения
COUNTRIES_DATA = [
    {"id": 1, "code": "RU", "name": "Российская Федерация"}
]

FEDERAL_DISTRICTS_DATA = [
    {"id": 1, "country_id": 1, "name": "Центральный федеральный округ"},
    {"id": 2, "country_id": 1, "name": "Северо-Западный федеральный округ"},
    {"id": 3, "country_id": 1, "name": "Южный федеральный округ"},
    {"id": 4, "country_id": 1, "name": "Приволжский федеральный округ"},
    {"id": 5, "country_id": 1, "name": "Уральский федеральный округ"},
    {"id": 6, "country_id": 1, "name": "Сибирский федеральный округ"},
    {"id": 7, "country_id": 1, "name": "Дальневосточный федеральный округ"},
    {"id": 8, "country_id": 1, "name": "Северо-Кавказский федеральный округ"}
]

# Основные регионы России
REGIONS_DATA = [
    # Центральный ФО
    {"id": 1, "district_id": 1, "country_id": 1, "name": "Московская область", "code": "MO"},
    {"id": 2, "district_id": 1, "country_id": 1, "name": "Москва", "code": "MOW"},
    {"id": 3, "district_id": 1, "country_id": 1, "name": "Белгородская область", "code": "BEL"},
    {"id": 4, "district_id": 1, "country_id": 1, "name": "Брянская область", "code": "BRY"},
    {"id": 5, "district_id": 1, "country_id": 1, "name": "Владимирская область", "code": "VLA"},
    {"id": 6, "district_id": 1, "country_id": 1, "name": "Воронежская область", "code": "VOR"},
    {"id": 7, "district_id": 1, "country_id": 1, "name": "Ивановская область", "code": "IVA"},
    {"id": 8, "district_id": 1, "country_id": 1, "name": "Калужская область", "code": "KLU"},
    {"id": 9, "district_id": 1, "country_id": 1, "name": "Костромская область", "code": "KOS"},
    {"id": 10, "district_id": 1, "country_id": 1, "name": "Курская область", "code": "KRS"},
    {"id": 11, "district_id": 1, "country_id": 1, "name": "Липецкая область", "code": "LIP"},
    {"id": 12, "district_id": 1, "country_id": 1, "name": "Орловская область", "code": "ORL"},
    {"id": 13, "district_id": 1, "country_id": 1, "name": "Рязанская область", "code": "RYA"},
    {"id": 14, "district_id": 1, "country_id": 1, "name": "Смоленская область", "code": "SMO"},
    {"id": 15, "district_id": 1, "country_id": 1, "name": "Тамбовская область", "code": "TAM"},
    {"id": 16, "district_id": 1, "country_id": 1, "name": "Тверская область", "code": "TVE"},
    {"id": 17, "district_id": 1, "country_id": 1, "name": "Тульская область", "code": "TUL"},
    {"id": 18, "district_id": 1, "country_id": 1, "name": "Ярославская область", "code": "YAR"},
    
    # Северо-Западный ФО
    {"id": 19, "district_id": 2, "country_id": 1, "name": "Санкт-Петербург", "code": "SPE"},
    {"id": 20, "district_id": 2, "country_id": 1, "name": "Ленинградская область", "code": "LEN"},
    {"id": 21, "district_id": 2, "country_id": 1, "name": "Архангельская область", "code": "ARK"},
    {"id": 22, "district_id": 2, "country_id": 1, "name": "Вологодская область", "code": "VLG"},
    {"id": 23, "district_id": 2, "country_id": 1, "name": "Калининградская область", "code": "KGD"},
    {"id": 24, "district_id": 2, "country_id": 1, "name": "Карелия", "code": "KR"},
    {"id": 25, "district_id": 2, "country_id": 1, "name": "Коми", "code": "KO"},
    {"id": 26, "district_id": 2, "country_id": 1, "name": "Мурманская область", "code": "MUR"},
    {"id": 27, "district_id": 2, "country_id": 1, "name": "Ненецкий автономный округ", "code": "NEN"},
    {"id": 28, "district_id": 2, "country_id": 1, "name": "Новгородская область", "code": "NGR"},
    {"id": 29, "district_id": 2, "country_id": 1, "name": "Псковская область", "code": "PSK"},
    
    # Южный ФО
    {"id": 30, "district_id": 3, "country_id": 1, "name": "Краснодарский край", "code": "KDA"},
    {"id": 31, "district_id": 3, "country_id": 1, "name": "Астраханская область", "code": "AST"},
    {"id": 32, "district_id": 3, "country_id": 1, "name": "Волгоградская область", "code": "VGG"},
    {"id": 33, "district_id": 3, "country_id": 1, "name": "Ростовская область", "code": "ROS"},
    {"id": 34, "district_id": 3, "country_id": 1, "name": "Республика Адыгея", "code": "AD"},
    {"id": 35, "district_id": 3, "country_id": 1, "name": "Республика Калмыкия", "code": "KL"},
    {"id": 36, "district_id": 3, "country_id": 1, "name": "Крым", "code": "CR"},
    {"id": 37, "district_id": 3, "country_id": 1, "name": "Севастополь", "code": "SEV"},
    
    # Приволжский ФО
    {"id": 38, "district_id": 4, "country_id": 1, "name": "Нижегородская область", "code": "NIZ"},
    {"id": 39, "district_id": 4, "country_id": 1, "name": "Кировская область", "code": "KIR"},
    {"id": 40, "district_id": 4, "country_id": 1, "name": "Самарская область", "code": "SAM"},
    {"id": 41, "district_id": 4, "country_id": 1, "name": "Саратовская область", "code": "SAR"},
    {"id": 42, "district_id": 4, "country_id": 1, "name": "Ульяновская область", "code": "ULY"},
    {"id": 43, "district_id": 4, "country_id": 1, "name": "Республика Башкортостан", "code": "BA"},
    {"id": 44, "district_id": 4, "country_id": 1, "name": "Республика Марий Эл", "code": "ME"},
    {"id": 45, "district_id": 4, "country_id": 1, "name": "Республика Мордовия", "code": "MO"},
    {"id": 46, "district_id": 4, "country_id": 1, "name": "Республика Татарстан", "code": "TA"},
    {"id": 47, "district_id": 4, "country_id": 1, "name": "Удмуртская Республика", "code": "UD"},
    {"id": 48, "district_id": 4, "country_id": 1, "name": "Чувашская Республика", "code": "CU"},
    {"id": 49, "district_id": 4, "country_id": 1, "name": "Пермский край", "code": "PER"},
    {"id": 50, "district_id": 4, "country_id": 1, "name": "Оренбургская область", "code": "ORE"},
    {"id": 51, "district_id": 4, "country_id": 1, "name": "Пензенская область", "code": "PNZ"},
    
    # Уральский ФО
    {"id": 52, "district_id": 5, "country_id": 1, "name": "Свердловская область", "code": "SVE"},
    {"id": 53, "district_id": 5, "country_id": 1, "name": "Тюменская область", "code": "TYU"},
    {"id": 54, "district_id": 5, "country_id": 1, "name": "Челябинская область", "code": "CHE"},
    {"id": 55, "district_id": 5, "country_id": 1, "name": "Ханты-Мансийский автономный округ", "code": "KHM"},
    {"id": 56, "district_id": 5, "country_id": 1, "name": "Ямало-Ненецкий автономный округ", "code": "YAN"},
    {"id": 57, "district_id": 5, "country_id": 1, "name": "Курганская область", "code": "KGN"},
    
    # Сибирский ФО
    {"id": 58, "district_id": 6, "country_id": 1, "name": "Новосибирская область", "code": "NVS"},
    {"id": 59, "district_id": 6, "country_id": 1, "name": "Красноярский край", "code": "KYA"},
    {"id": 60, "district_id": 6, "country_id": 1, "name": "Иркутская область", "code": "IRK"},
    {"id": 61, "district_id": 6, "country_id": 1, "name": "Кемеровская область", "code": "KEM"},
    {"id": 62, "district_id": 6, "country_id": 1, "name": "Омская область", "code": "OMS"},
    {"id": 63, "district_id": 6, "country_id": 1, "name": "Томская область", "code": "TOM"},
    {"id": 64, "district_id": 6, "country_id": 1, "name": "Алтайский край", "code": "ALT"},
    {"id": 65, "district_id": 6, "country_id": 1, "name": "Республика Алтай", "code": "AL"},
    {"id": 66, "district_id": 6, "country_id": 1, "name": "Республика Бурятия", "code": "BU"},
    {"id": 67, "district_id": 6, "country_id": 1, "name": "Республика Тыва", "code": "TY"},
    {"id": 68, "district_id": 6, "country_id": 1, "name": "Республика Хакасия", "code": "KK"},
    {"id": 69, "district_id": 6, "country_id": 1, "name": "Забайкальский край", "code": "ZAB"},
    
    # Дальневосточный ФО
    {"id": 70, "district_id": 7, "country_id": 1, "name": "Приморский край", "code": "PRI"},
    {"id": 71, "district_id": 7, "country_id": 1, "name": "Хабаровский край", "code": "KHA"},
    {"id": 72, "district_id": 7, "country_id": 1, "name": "Амурская область", "code": "AMU"},
    {"id": 73, "district_id": 7, "country_id": 1, "name": "Камчатский край", "code": "KAM"},
    {"id": 74, "district_id": 7, "country_id": 1, "name": "Магаданская область", "code": "MAG"},
    {"id": 75, "district_id": 7, "country_id": 1, "name": "Сахалинская область", "code": "SAK"},
    {"id": 76, "district_id": 7, "country_id": 1, "name": "Еврейская автономная область", "code": "YEV"},
    {"id": 77, "district_id": 7, "country_id": 1, "name": "Чукотский автономный округ", "code": "CHU"},
    {"id": 78, "district_id": 7, "country_id": 1, "name": "Республика Саха (Якутия)", "code": "SA"},
    
    # Северо-Кавказский ФО
    {"id": 79, "district_id": 8, "country_id": 1, "name": "Ставропольский край", "code": "STA"},
    {"id": 80, "district_id": 8, "country_id": 1, "name": "Республика Дагестан", "code": "DA"},
    {"id": 81, "district_id": 8, "country_id": 1, "name": "Республика Ингушетия", "code": "IN"},
    {"id": 82, "district_id": 8, "country_id": 1, "name": "Кабардино-Балкарская Республика", "code": "KB"},
    {"id": 83, "district_id": 8, "country_id": 1, "name": "Карачаево-Черкесская Республика", "code": "KC"},
    {"id": 84, "district_id": 8, "country_id": 1, "name": "Республика Северная Осетия", "code": "SE"},
    {"id": 85, "district_id": 8, "country_id": 1, "name": "Чеченская Республика", "code": "CE"}
]

# Основные города России (города-миллионники и региональные центры)
CITIES_DATA = [
    # Города-миллионники
    {"id": 1, "country_id": 1, "region_id": 2, "federal_district_id": 1, "name": "Москва", "population": 12692466, "is_million_city": True, "is_regional_center": True},
    {"id": 2, "country_id": 1, "region_id": 19, "federal_district_id": 2, "name": "Санкт-Петербург", "population": 5383890, "is_million_city": True, "is_regional_center": True},
    {"id": 3, "country_id": 1, "region_id": 58, "federal_district_id": 6, "name": "Новосибирск", "population": 1633595, "is_million_city": True, "is_regional_center": True},
    {"id": 4, "country_id": 1, "region_id": 43, "federal_district_id": 4, "name": "Екатеринбург", "population": 1544376, "is_million_city": True, "is_regional_center": True},
    {"id": 5, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Казань", "population": 1308660, "is_million_city": True, "is_regional_center": True},
    {"id": 6, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Нижний Новгород", "population": 1244251, "is_million_city": True, "is_regional_center": True},
    {"id": 7, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Челябинск", "population": 1202371, "is_million_city": True, "is_regional_center": True},
    {"id": 8, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Самара", "population": 1156659, "is_million_city": True, "is_regional_center": True},
    {"id": 9, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Омск", "population": 1125695, "is_million_city": True, "is_regional_center": True},
    {"id": 10, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Ростов-на-Дону", "population": 1120482, "is_million_city": True, "is_regional_center": True},
    {"id": 11, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Уфа", "population": 1115560, "is_million_city": True, "is_regional_center": True},
    {"id": 12, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Красноярск", "population": 1093861, "is_million_city": True, "is_regional_center": True},
    {"id": 13, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Воронеж", "population": 1057681, "is_million_city": True, "is_regional_center": True},
    {"id": 14, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Пермь", "population": 1051551, "is_million_city": True, "is_regional_center": True},
    {"id": 15, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Волгоград", "population": 1028036, "is_million_city": True, "is_regional_center": True},
    
    # Крупные региональные центры
    {"id": 16, "country_id": 1, "region_id": 1, "federal_district_id": 1, "name": "Подольск", "population": 309000, "is_million_city": False, "is_regional_center": False},
    {"id": 17, "country_id": 1, "region_id": 1, "federal_district_id": 1, "name": "Химки", "population": 250000, "is_million_city": False, "is_regional_center": False},
    {"id": 18, "country_id": 1, "region_id": 1, "federal_district_id": 1, "name": "Королёв", "population": 220000, "is_million_city": False, "is_regional_center": False},
    {"id": 19, "country_id": 1, "region_id": 1, "federal_district_id": 1, "name": "Мытищи", "population": 210000, "is_million_city": False, "is_regional_center": False},
    {"id": 20, "country_id": 1, "region_id": 1, "federal_district_id": 1, "name": "Люберцы", "population": 200000, "is_million_city": False, "is_regional_center": False},
    
    # Санкт-Петербург и область
    {"id": 21, "country_id": 1, "region_id": 20, "federal_district_id": 2, "name": "Гатчина", "population": 95000, "is_million_city": False, "is_regional_center": False},
    {"id": 22, "country_id": 1, "region_id": 20, "federal_district_id": 2, "name": "Выборг", "population": 80000, "is_million_city": False, "is_regional_center": False},
    {"id": 23, "country_id": 1, "region_id": 20, "federal_district_id": 2, "name": "Сосновый Бор", "population": 70000, "is_million_city": False, "is_regional_center": False},
    
    # Краснодарский край
    {"id": 24, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Краснодар", "population": 950000, "is_million_city": False, "is_regional_center": True},
    {"id": 25, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Сочи", "population": 450000, "is_million_city": False, "is_regional_center": False},
    {"id": 26, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Армавир", "population": 190000, "is_million_city": False, "is_regional_center": False},
    {"id": 27, "country_id": 1, "region_id": 30, "federal_district_id": 3, "name": "Новороссийск", "population": 280000, "is_million_city": False, "is_regional_center": False},
    
    # Свердловская область
    {"id": 28, "country_id": 1, "region_id": 52, "federal_district_id": 5, "name": "Нижний Тагил", "population": 350000, "is_million_city": False, "is_regional_center": False},
    {"id": 29, "country_id": 1, "region_id": 52, "federal_district_id": 5, "name": "Каменск-Уральский", "population": 170000, "is_million_city": False, "is_regional_center": False},
    
    # Татарстан
    {"id": 30, "country_id": 1, "region_id": 46, "federal_district_id": 4, "name": "Набережные Челны", "population": 550000, "is_million_city": False, "is_regional_center": False},
    {"id": 31, "country_id": 1, "region_id": 46, "federal_district_id": 4, "name": "Альметьевск", "population": 160000, "is_million_city": False, "is_regional_center": False},
    
    # Башкортостан
    {"id": 32, "country_id": 1, "region_id": 43, "federal_district_id": 4, "name": "Стерлитамак", "population": 280000, "is_million_city": False, "is_regional_center": False},
    {"id": 33, "country_id": 1, "region_id": 43, "federal_district_id": 4, "name": "Салават", "population": 150000, "is_million_city": False, "is_regional_center": False},
    
    # Красноярский край
    {"id": 34, "country_id": 1, "region_id": 59, "federal_district_id": 6, "name": "Норильск", "population": 180000, "is_million_city": False, "is_regional_center": False},
    {"id": 35, "country_id": 1, "region_id": 59, "federal_district_id": 6, "name": "Ачинск", "population": 100000, "is_million_city": False, "is_regional_center": False},
    
    # Приморский край
    {"id": 36, "country_id": 1, "region_id": 70, "federal_district_id": 7, "name": "Владивосток", "population": 600000, "is_million_city": False, "is_regional_center": True},
    {"id": 37, "country_id": 1, "region_id": 70, "federal_district_id": 7, "name": "Находка", "population": 150000, "is_million_city": False, "is_regional_center": False},
    
    # Хабаровский край
    {"id": 38, "country_id": 1, "region_id": 71, "federal_district_id": 7, "name": "Хабаровск", "population": 620000, "is_million_city": False, "is_regional_center": True},
    {"id": 39, "country_id": 1, "region_id": 71, "federal_district_id": 7, "name": "Комсомольск-на-Амуре", "population": 240000, "is_million_city": False, "is_regional_center": False},
    
    # Иркутская область
    {"id": 40, "country_id": 1, "region_id": 60, "federal_district_id": 6, "name": "Иркутск", "population": 620000, "is_million_city": False, "is_regional_center": True},
    {"id": 41, "country_id": 1, "region_id": 60, "federal_district_id": 6, "name": "Братск", "population": 230000, "is_million_city": False, "is_regional_center": False},
    
    # Кемеровская область
    {"id": 42, "country_id": 1, "region_id": 61, "federal_district_id": 6, "name": "Кемерово", "population": 550000, "is_million_city": False, "is_regional_center": True},
    {"id": 43, "country_id": 1, "region_id": 61, "federal_district_id": 6, "name": "Новокузнецк", "population": 540000, "is_million_city": False, "is_regional_center": False},
    
    # Томская область
    {"id": 44, "country_id": 1, "region_id": 63, "federal_district_id": 6, "name": "Томск", "population": 570000, "is_million_city": False, "is_regional_center": True},
    
    # Алтайский край
    {"id": 45, "country_id": 1, "region_id": 64, "federal_district_id": 6, "name": "Барнаул", "population": 630000, "is_million_city": False, "is_regional_center": True},
    {"id": 46, "country_id": 1, "region_id": 64, "federal_district_id": 6, "name": "Бийск", "population": 200000, "is_million_city": False, "is_regional_center": False},
    
    # Самарская область
    {"id": 47, "country_id": 1, "region_id": 40, "federal_district_id": 4, "name": "Тольятти", "population": 700000, "is_million_city": False, "is_regional_center": False},
    {"id": 48, "country_id": 1, "region_id": 40, "federal_district_id": 4, "name": "Сызрань", "population": 170000, "is_million_city": False, "is_regional_center": False},
    
    # Нижегородская область
    {"id": 49, "country_id": 1, "region_id": 38, "federal_district_id": 4, "name": "Дзержинск", "population": 230000, "is_million_city": False, "is_regional_center": False},
    {"id": 50, "country_id": 1, "region_id": 38, "federal_district_id": 4, "name": "Арзамас", "population": 100000, "is_million_city": False, "is_regional_center": False},
    
    # Саратовская область
    {"id": 51, "country_id": 1, "region_id": 41, "federal_district_id": 4, "name": "Энгельс", "population": 220000, "is_million_city": False, "is_regional_center": False},
    {"id": 52, "country_id": 1, "region_id": 41, "federal_district_id": 4, "name": "Балаково", "population": 190000, "is_million_city": False, "is_regional_center": False},
    
    # Волгоградская область
    {"id": 53, "country_id": 1, "region_id": 32, "federal_district_id": 3, "name": "Волжский", "population": 320000, "is_million_city": False, "is_regional_center": False},
    {"id": 54, "country_id": 1, "region_id": 32, "federal_district_id": 3, "name": "Камышин", "population": 110000, "is_million_city": False, "is_regional_center": False},
    
    # Ростовская область
    {"id": 55, "country_id": 1, "region_id": 33, "federal_district_id": 3, "name": "Таганрог", "population": 250000, "is_million_city": False, "is_regional_center": False},
    {"id": 56, "country_id": 1, "region_id": 33, "federal_district_id": 3, "name": "Шахты", "population": 230000, "is_million_city": False, "is_regional_center": False},
    
    # Воронежская область
    {"id": 57, "country_id": 1, "region_id": 6, "federal_district_id": 1, "name": "Борисоглебск", "population": 60000, "is_million_city": False, "is_regional_center": False},
    {"id": 58, "country_id": 1, "region_id": 6, "federal_district_id": 1, "name": "Россошь", "population": 60000, "is_million_city": False, "is_regional_center": False},
    
    # Тюменская область
    {"id": 59, "country_id": 1, "region_id": 53, "federal_district_id": 5, "name": "Тюмень", "population": 850000, "is_million_city": False, "is_regional_center": True},
    {"id": 60, "country_id": 1, "region_id": 53, "federal_district_id": 5, "name": "Тобольск", "population": 100000, "is_million_city": False, "is_regional_center": False},
    
    # Ханты-Мансийский АО
    {"id": 61, "country_id": 1, "region_id": 55, "federal_district_id": 5, "name": "Сургут", "population": 380000, "is_million_city": False, "is_regional_center": False},
    {"id": 62, "country_id": 1, "region_id": 55, "federal_district_id": 5, "name": "Нижневартовск", "population": 280000, "is_million_city": False, "is_regional_center": False},
    
    # Ямало-Ненецкий АО
    {"id": 63, "country_id": 1, "region_id": 56, "federal_district_id": 5, "name": "Новый Уренгой", "population": 120000, "is_million_city": False, "is_regional_center": False},
    {"id": 64, "country_id": 1, "region_id": 56, "federal_district_id": 5, "name": "Салехард", "population": 50000, "is_million_city": False, "is_regional_center": False},
    
    # Ставропольский край
    {"id": 65, "country_id": 1, "region_id": 79, "federal_district_id": 8, "name": "Ставрополь", "population": 450000, "is_million_city": False, "is_regional_center": True},
    {"id": 66, "country_id": 1, "region_id": 79, "federal_district_id": 8, "name": "Пятигорск", "population": 140000, "is_million_city": False, "is_regional_center": False},
    
    # Республика Дагестан
    {"id": 67, "country_id": 1, "region_id": 80, "federal_district_id": 8, "name": "Махачкала", "population": 600000, "is_million_city": False, "is_regional_center": True},
    {"id": 68, "country_id": 1, "region_id": 80, "federal_district_id": 8, "name": "Дербент", "population": 120000, "is_million_city": False, "is_regional_center": False},
    
    # Чеченская Республика
    {"id": 69, "country_id": 1, "region_id": 85, "federal_district_id": 8, "name": "Грозный", "population": 300000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Северная Осетия
    {"id": 70, "country_id": 1, "region_id": 84, "federal_district_id": 8, "name": "Владикавказ", "population": 300000, "is_million_city": False, "is_regional_center": True},
    
    # Кабардино-Балкарская Республика
    {"id": 71, "country_id": 1, "region_id": 82, "federal_district_id": 8, "name": "Нальчик", "population": 240000, "is_million_city": False, "is_regional_center": True},
    
    # Карачаево-Черкесская Республика
    {"id": 72, "country_id": 1, "region_id": 83, "federal_district_id": 8, "name": "Черкесск", "population": 120000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Ингушетия
    {"id": 73, "country_id": 1, "region_id": 81, "federal_district_id": 8, "name": "Магас", "population": 10000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Адыгея
    {"id": 74, "country_id": 1, "region_id": 34, "federal_district_id": 3, "name": "Майкоп", "population": 140000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Калмыкия
    {"id": 75, "country_id": 1, "region_id": 35, "federal_district_id": 3, "name": "Элиста", "population": 100000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Саха (Якутия)
    {"id": 76, "country_id": 1, "region_id": 78, "federal_district_id": 7, "name": "Якутск", "population": 350000, "is_million_city": False, "is_regional_center": True},
    {"id": 77, "country_id": 1, "region_id": 78, "federal_district_id": 7, "name": "Нерюнгри", "population": 60000, "is_million_city": False, "is_regional_center": False},
    
    # Камчатский край
    {"id": 78, "country_id": 1, "region_id": 73, "federal_district_id": 7, "name": "Петропавловск-Камчатский", "population": 180000, "is_million_city": False, "is_regional_center": True},
    
    # Магаданская область
    {"id": 79, "country_id": 1, "region_id": 74, "federal_district_id": 7, "name": "Магадан", "population": 90000, "is_million_city": False, "is_regional_center": True},
    
    # Сахалинская область
    {"id": 80, "country_id": 1, "region_id": 75, "federal_district_id": 7, "name": "Южно-Сахалинск", "population": 200000, "is_million_city": False, "is_regional_center": True},
    
    # Еврейская автономная область
    {"id": 81, "country_id": 1, "region_id": 76, "federal_district_id": 7, "name": "Биробиджан", "population": 70000, "is_million_city": False, "is_regional_center": True},
    
    # Чукотский автономный округ
    {"id": 82, "country_id": 1, "region_id": 77, "federal_district_id": 7, "name": "Анадырь", "population": 15000, "is_million_city": False, "is_regional_center": True},
    
    # Амурская область
    {"id": 83, "country_id": 1, "region_id": 72, "federal_district_id": 7, "name": "Благовещенск", "population": 240000, "is_million_city": False, "is_regional_center": True},
    {"id": 84, "country_id": 1, "region_id": 72, "federal_district_id": 7, "name": "Белогорск", "population": 60000, "is_million_city": False, "is_regional_center": False},
    
    # Республика Бурятия
    {"id": 85, "country_id": 1, "region_id": 66, "federal_district_id": 6, "name": "Улан-Удэ", "population": 440000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Тыва
    {"id": 86, "country_id": 1, "region_id": 67, "federal_district_id": 6, "name": "Кызыл", "population": 120000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Хакасия
    {"id": 87, "country_id": 1, "region_id": 68, "federal_district_id": 6, "name": "Абакан", "population": 180000, "is_million_city": False, "is_regional_center": True},
    
    # Забайкальский край
    {"id": 88, "country_id": 1, "region_id": 69, "federal_district_id": 6, "name": "Чита", "population": 350000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Алтай
    {"id": 89, "country_id": 1, "region_id": 65, "federal_district_id": 6, "name": "Горно-Алтайск", "population": 65000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Марий Эл
    {"id": 90, "country_id": 1, "region_id": 44, "federal_district_id": 4, "name": "Йошкар-Ола", "population": 280000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Мордовия
    {"id": 91, "country_id": 1, "region_id": 45, "federal_district_id": 4, "name": "Саранск", "population": 320000, "is_million_city": False, "is_regional_center": True},
    
    # Удмуртская Республика
    {"id": 92, "country_id": 1, "region_id": 47, "federal_district_id": 4, "name": "Ижевск", "population": 650000, "is_million_city": False, "is_regional_center": True},
    
    # Чувашская Республика
    {"id": 93, "country_id": 1, "region_id": 48, "federal_district_id": 4, "name": "Чебоксары", "population": 500000, "is_million_city": False, "is_regional_center": True},
    
    # Пермский край
    {"id": 94, "country_id": 1, "region_id": 49, "federal_district_id": 4, "name": "Березники", "population": 140000, "is_million_city": False, "is_regional_center": False},
    
    # Оренбургская область
    {"id": 95, "country_id": 1, "region_id": 50, "federal_district_id": 4, "name": "Оренбург", "population": 570000, "is_million_city": False, "is_regional_center": True},
    {"id": 96, "country_id": 1, "region_id": 50, "federal_district_id": 4, "name": "Орск", "population": 220000, "is_million_city": False, "is_regional_center": False},
    
    # Пензенская область
    {"id": 97, "country_id": 1, "region_id": 51, "federal_district_id": 4, "name": "Пенза", "population": 520000, "is_million_city": False, "is_regional_center": True},
    
    # Курганская область
    {"id": 98, "country_id": 1, "region_id": 57, "federal_district_id": 5, "name": "Курган", "population": 320000, "is_million_city": False, "is_regional_center": True},
    
    # Архангельская область
    {"id": 99, "country_id": 1, "region_id": 21, "federal_district_id": 2, "name": "Архангельск", "population": 350000, "is_million_city": False, "is_regional_center": True},
    {"id": 100, "country_id": 1, "region_id": 21, "federal_district_id": 2, "name": "Северодвинск", "population": 180000, "is_million_city": False, "is_regional_center": False},
    
    # Вологодская область
    {"id": 101, "country_id": 1, "region_id": 22, "federal_district_id": 2, "name": "Вологда", "population": 320000, "is_million_city": False, "is_regional_center": True},
    {"id": 102, "country_id": 1, "region_id": 22, "federal_district_id": 2, "name": "Череповец", "population": 310000, "is_million_city": False, "is_regional_center": False},
    
    # Калининградская область
    {"id": 103, "country_id": 1, "region_id": 23, "federal_district_id": 2, "name": "Калининград", "population": 490000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Карелия
    {"id": 104, "country_id": 1, "region_id": 24, "federal_district_id": 2, "name": "Петрозаводск", "population": 280000, "is_million_city": False, "is_regional_center": True},
    
    # Республика Коми
    {"id": 105, "country_id": 1, "region_id": 25, "federal_district_id": 2, "name": "Сыктывкар", "population": 250000, "is_million_city": False, "is_regional_center": True},
    
    # Мурманская область
    {"id": 106, "country_id": 1, "region_id": 26, "federal_district_id": 2, "name": "Мурманск", "population": 280000, "is_million_city": False, "is_regional_center": True},
    
    # Новгородская область
    {"id": 107, "country_id": 1, "region_id": 28, "federal_district_id": 2, "name": "Великий Новгород", "population": 220000, "is_million_city": False, "is_regional_center": True},
    
    # Псковская область
    {"id": 108, "country_id": 1, "region_id": 29, "federal_district_id": 2, "name": "Псков", "population": 200000, "is_million_city": False, "is_regional_center": True},
    
    # Ярославская область
    {"id": 109, "country_id": 1, "region_id": 18, "federal_district_id": 1, "name": "Ярославль", "population": 600000, "is_million_city": False, "is_regional_center": True},
    {"id": 110, "country_id": 1, "region_id": 18, "federal_district_id": 1, "name": "Рыбинск", "population": 180000, "is_million_city": False, "is_regional_center": False},
    
    # Тверская область
    {"id": 111, "country_id": 1, "region_id": 16, "federal_district_id": 1, "name": "Тверь", "population": 420000, "is_million_city": False, "is_regional_center": True},
    
    # Тульская область
    {"id": 112, "country_id": 1, "region_id": 17, "federal_district_id": 1, "name": "Тула", "population": 470000, "is_million_city": False, "is_regional_center": True},
    
    # Рязанская область
    {"id": 113, "country_id": 1, "region_id": 13, "federal_district_id": 1, "name": "Рязань", "population": 540000, "is_million_city": False, "is_regional_center": True},
    
    # Смоленская область
    {"id": 114, "country_id": 1, "region_id": 14, "federal_district_id": 1, "name": "Смоленск", "population": 320000, "is_million_city": False, "is_regional_center": True},
    
    # Тамбовская область
    {"id": 115, "country_id": 1, "region_id": 15, "federal_district_id": 1, "name": "Тамбов", "population": 290000, "is_million_city": False, "is_regional_center": True},
    
    # Орловская область
    {"id": 116, "country_id": 1, "region_id": 12, "federal_district_id": 1, "name": "Орёл", "population": 300000, "is_million_city": False, "is_regional_center": True},
    
    # Курская область
    {"id": 117, "country_id": 1, "region_id": 10, "federal_district_id": 1, "name": "Курск", "population": 450000, "is_million_city": False, "is_regional_center": True},
    
    # Липецкая область
    {"id": 118, "country_id": 1, "region_id": 11, "federal_district_id": 1, "name": "Липецк", "population": 510000, "is_million_city": False, "is_regional_center": True},
    
    # Калужская область
    {"id": 119, "country_id": 1, "region_id": 8, "federal_district_id": 1, "name": "Калуга", "population": 340000, "is_million_city": False, "is_regional_center": True},
    
    # Брянская область
    {"id": 120, "country_id": 1, "region_id": 4, "federal_district_id": 1, "name": "Брянск", "population": 400000, "is_million_city": False, "is_regional_center": True},
    
    # Владимирская область
    {"id": 121, "country_id": 1, "region_id": 5, "federal_district_id": 1, "name": "Владимир", "population": 350000, "is_million_city": False, "is_regional_center": True},
    
    # Ивановская область
    {"id": 122, "country_id": 1, "region_id": 7, "federal_district_id": 1, "name": "Иваново", "population": 400000, "is_million_city": False, "is_regional_center": True},
    
    # Костромская область
    {"id": 123, "country_id": 1, "region_id": 9, "federal_district_id": 1, "name": "Кострома", "population": 270000, "is_million_city": False, "is_regional_center": True},
    
    # Белгородская область
    {"id": 124, "country_id": 1, "region_id": 3, "federal_district_id": 1, "name": "Белгород", "population": 390000, "is_million_city": False, "is_regional_center": True},
    
    # Астраханская область
    {"id": 125, "country_id": 1, "region_id": 31, "federal_district_id": 3, "name": "Астрахань", "population": 530000, "is_million_city": False, "is_regional_center": True},
    
    # Крым
    {"id": 126, "country_id": 1, "region_id": 36, "federal_district_id": 3, "name": "Симферополь", "population": 340000, "is_million_city": False, "is_regional_center": True},
    {"id": 127, "country_id": 1, "region_id": 36, "federal_district_id": 3, "name": "Севастополь", "population": 520000, "is_million_city": False, "is_regional_center": True},
    {"id": 128, "country_id": 1, "region_id": 36, "federal_district_id": 3, "name": "Керчь", "population": 150000, "is_million_city": False, "is_regional_center": False},
    {"id": 129, "country_id": 1, "region_id": 36, "federal_district_id": 3, "name": "Евпатория", "population": 100000, "is_million_city": False, "is_regional_center": False},
    {"id": 130, "country_id": 1, "region_id": 36, "federal_district_id": 3, "name": "Ялта", "population": 80000, "is_million_city": False, "is_regional_center": False},
    
    # Ульяновская область
    {"id": 131, "country_id": 1, "region_id": 42, "federal_district_id": 4, "name": "Ульяновск", "population": 620000, "is_million_city": False, "is_regional_center": True},
    {"id": 132, "country_id": 1, "region_id": 42, "federal_district_id": 4, "name": "Димитровград", "population": 110000, "is_million_city": False, "is_regional_center": False},
    
    # Кировская область
    {"id": 133, "country_id": 1, "region_id": 39, "federal_district_id": 4, "name": "Киров", "population": 500000, "is_million_city": False, "is_regional_center": True},
    
    # Ненецкий автономный округ
    {"id": 134, "country_id": 1, "region_id": 27, "federal_district_id": 2, "name": "Нарьян-Мар", "population": 25000, "is_million_city": False, "is_regional_center": True},
]


class DatabasePopulator:
    def __init__(self):
        self.connection = None
        
    async def connect(self):
        """Подключение к базе данных"""
        database_url = os.getenv("SQLALCHEMY_DATABASE_URL", "postgresql://postgres:postgres@localhost/postgres")
        self.connection = await asyncpg.connect(database_url)
        logger.info("Подключение к базе данных установлено")
        
    async def disconnect(self):
        """Отключение от базы данных"""
        if self.connection:
            await self.connection.close()
            logger.info("Соединение с базой данных закрыто")
    
    async def clear_tables(self):
        """Очистка таблиц в правильном порядке"""
        logger.info("Очистка существующих данных...")
        
        # Удаляем в обратном порядке зависимостей
        tables_to_clear = ["cities", "regions", "federal_districts", "countries"]
        
        for table in tables_to_clear:
            try:
                await self.connection.execute(f"DELETE FROM {table}")
                logger.info(f"Очищена таблица {table}")
            except Exception as e:
                logger.warning(f"Не удалось очистить таблицу {table}: {e}")
    
    async def populate_countries(self):
        """Заполнение таблицы стран"""
        logger.info("Заполнение таблицы стран...")
        
        for country in COUNTRIES_DATA:
            await self.connection.execute("""
                INSERT INTO countries (id, code, name, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    code = EXCLUDED.code,
                    name = EXCLUDED.name,
                    is_active = EXCLUDED.is_active,
                    updated_at = NOW()
            """, country["id"], country["code"], country["name"], True)
        
        logger.info(f"Добавлено {len(COUNTRIES_DATA)} стран")
    
    async def populate_federal_districts(self):
        """Заполнение таблицы федеральных округов"""
        logger.info("Заполнение таблицы федеральных округов...")
        
        for district in FEDERAL_DISTRICTS_DATA:
            await self.connection.execute("""
                INSERT INTO federal_districts (id, country_id, name, code, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    country_id = EXCLUDED.country_id,
                    name = EXCLUDED.name,
                    code = EXCLUDED.code,
                    is_active = EXCLUDED.is_active,
                    updated_at = NOW()
            """, district["id"], district["country_id"], district["name"], f"FD{district['id']}", True)
        
        logger.info(f"Добавлено {len(FEDERAL_DISTRICTS_DATA)} федеральных округов")
    
    async def populate_regions(self):
        """Заполнение таблицы регионов"""
        logger.info("Заполнение таблицы регионов...")
        
        for region in REGIONS_DATA:
            await self.connection.execute("""
                INSERT INTO regions (id, country_id, federal_district_id, name, code, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    country_id = EXCLUDED.country_id,
                    federal_district_id = EXCLUDED.federal_district_id,
                    name = EXCLUDED.name,
                    code = EXCLUDED.code,
                    is_active = EXCLUDED.is_active,
                    updated_at = NOW()
            """, region["id"], region["country_id"], region["district_id"], region["name"], region["code"], True)
        
        logger.info(f"Добавлено {len(REGIONS_DATA)} регионов")
    
    async def populate_cities(self):
        """Заполнение таблицы городов"""
        logger.info("Заполнение таблицы городов...")
        
        for city in CITIES_DATA:
            await self.connection.execute("""
                INSERT INTO cities (id, country_id, region_id, federal_district_id, name, population, 
                                 is_million_city, is_regional_center, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    country_id = EXCLUDED.country_id,
                    region_id = EXCLUDED.region_id,
                    federal_district_id = EXCLUDED.federal_district_id,
                    name = EXCLUDED.name,
                    population = EXCLUDED.population,
                    is_million_city = EXCLUDED.is_million_city,
                    is_regional_center = EXCLUDED.is_regional_center,
                    is_active = EXCLUDED.is_active,
                    updated_at = NOW()
            """, city["id"], city["country_id"], city["region_id"], city["federal_district_id"], 
                city["name"], city["population"], city["is_million_city"], 
                city["is_regional_center"], True)
        
        logger.info(f"Добавлено {len(CITIES_DATA)} городов")
    
    async def populate_all(self):
        """Заполнение всех таблиц"""
        try:
            await self.connect()
            await self.clear_tables()
            
            await self.populate_countries()
            await self.populate_federal_districts()
            await self.populate_regions()
            await self.populate_cities()
            
            logger.info("База данных успешно заполнена!")
            
        except Exception as e:
            logger.error(f"Ошибка при заполнении базы данных: {e}")
            raise
        finally:
            await self.disconnect()


async def main():
    """Основная функция"""
    populator = DatabasePopulator()
    await populator.populate_all()


if __name__ == "__main__":
    asyncio.run(main())
