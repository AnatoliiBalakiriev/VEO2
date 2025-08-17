#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфігурація для агента пошуку квитків Укрзалізниці
"""

import os
from typing import Dict, List

# Налаштування браузера
BROWSER_CONFIG = {
    "headless": False,  # Запуск браузера в фоновому режимі
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "timeout": 10,  # Таймаут очікування елементів (секунди)
    "page_load_timeout": 30,  # Таймаут завантаження сторінки
    "implicit_wait": 5,  # Неявне очікування елементів
}

# Налаштування пошуку
SEARCH_CONFIG = {
    "base_url": "https://booking.uz.gov.ua/",
    "delay_between_searches": 2,  # Затримка між пошуками (секунди)
    "max_retries": 3,  # Максимальна кількість спроб
    "retry_delay": 5,  # Затримка між спробами (секунди)
}

# Популярні маршрути для швидкого доступу
POPULAR_ROUTES = [
    ("Київ", "Львів"),
    ("Київ", "Харків"),
    ("Київ", "Одеса"),
    ("Київ", "Дніпро"),
    ("Львів", "Київ"),
    ("Харків", "Київ"),
    ("Одеса", "Київ"),
    ("Дніпро", "Київ"),
    ("Львів", "Одеса"),
    ("Харків", "Одеса"),
]

# Налаштування фільтрації
FILTER_CONFIG = {
    "price_ranges": [
        {"name": "Дуже дешево", "max_price": 500},
        {"name": "Дешево", "max_price": 1000},
        {"name": "Середня ціна", "max_price": 2000},
        {"name": "Дорого", "max_price": 5000},
        {"name": "Дуже дорого", "min_price": 5000},
    ],
    "time_ranges": [
        {"name": "Нічні поїзди", "start": 22, "end": 6},
        {"name": "Ранкові поїзди", "start": 6, "end": 12},
        {"name": "Денні поїзди", "start": 12, "end": 18},
        {"name": "Вечірні поїзди", "start": 18, "end": 22},
    ],
    "train_types": [
        "Швидкий",
        "Пасажирський",
        "Електричка",
        "Експрес",
        "Нічний",
    ]
}

# Налаштування логування
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "ukrzaliznytsia.log",
    "encoding": "utf-8",
    "max_file_size": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5,
}

# Налаштування збереження результатів
SAVE_CONFIG = {
    "default_format": "json",  # json, csv, txt
    "auto_save": True,
    "filename_template": "tickets_{timestamp}",
    "include_metadata": True,
    "compress_results": False,
}

# CSS селектори для парсингу (можуть змінюватися при оновленні сайту)
CSS_SELECTORS = {
    "search_form": {
        "from_station": "input[placeholder*='Звідки']",
        "to_station": "input[placeholder*='Куди']",
        "date": "input[type='date']",
        "search_button": "button[type='submit']",
    },
    "results": {
        "train_list": ".train-list",
        "train_item": ".train-item",
        "train_number": ".train-number",
        "station_name": ".station-name",
        "time": ".time",
        "travel_time": ".travel-time",
        "price": ".price",
        "seats": ".seats",
        "train_type": ".train-type",
        "station_suggest": ".station-suggest-item",
    },
    "pagination": {
        "next_page": ".pagination-next",
        "page_number": ".page-number",
    }
}

# Налаштування проксі (опціонально)
PROXY_CONFIG = {
    "use_proxy": False,
    "proxy_list": [
        # "http://proxy1:port",
        # "http://proxy2:port",
    ],
    "rotate_proxies": True,
    "proxy_timeout": 10,
}

# Налаштування уведення
INPUT_CONFIG = {
    "default_date_format": "%d.%m.%Y",
    "date_aliases": {
        "сьогодні": 0,
        "завтра": 1,
        "післязавтра": 2,
        "через тиждень": 7,
        "через місяць": 30,
    },
    "station_autocomplete": True,
    "max_station_suggestions": 10,
}

# Налаштування безпеки
SECURITY_CONFIG = {
    "rate_limiting": True,
    "max_requests_per_minute": 30,
    "respect_robots_txt": True,
    "random_delays": True,
    "min_delay": 1,
    "max_delay": 5,
}

def get_config() -> Dict:
    """Отримання всієї конфігурації"""
    return {
        "browser": BROWSER_CONFIG,
        "search": SEARCH_CONFIG,
        "popular_routes": POPULAR_ROUTES,
        "filters": FILTER_CONFIG,
        "logging": LOGGING_CONFIG,
        "save": SAVE_CONFIG,
        "css_selectors": CSS_SELECTORS,
        "proxy": PROXY_CONFIG,
        "input": INPUT_CONFIG,
        "security": SECURITY_CONFIG,
    }

def update_config_from_env():
    """Оновлення конфігурації з змінних середовища"""
    global BROWSER_CONFIG, SEARCH_CONFIG
    
    # Браузер
    if os.getenv("HEADLESS"):
        BROWSER_CONFIG["headless"] = os.getenv("HEADLESS").lower() == "true"
    
    if os.getenv("BROWSER_TIMEOUT"):
        BROWSER_CONFIG["timeout"] = int(os.getenv("BROWSER_TIMEOUT"))
    
    # Пошук
    if os.getenv("SEARCH_DELAY"):
        SEARCH_CONFIG["delay_between_searches"] = int(os.getenv("SEARCH_DELAY"))
    
    if os.getenv("MAX_RETRIES"):
        SEARCH_CONFIG["max_retries"] = int(os.getenv("MAX_RETRIES"))

def validate_config() -> List[str]:
    """Валідація конфігурації"""
    errors = []
    
    # Перевірка таймаутів
    if BROWSER_CONFIG["timeout"] <= 0:
        errors.append("Таймаут браузера має бути більше 0")
    
    if SEARCH_CONFIG["delay_between_searches"] < 0:
        errors.append("Затримка між пошуками не може бути від'ємною")
    
    # Перевірка URL
    if not SEARCH_CONFIG["base_url"].startswith("http"):
        errors.append("Базовий URL має починатися з http/https")
    
    return errors

# Оновлення конфігурації з змінних середовища при імпорті
update_config_from_env()

# Валідація конфігурації
if __name__ == "__main__":
    errors = validate_config()
    if errors:
        print("Помилки в конфігурації:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Конфігурація валідна")