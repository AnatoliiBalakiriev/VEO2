#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Покращений агент для пошуку квитків на сайті Укрзалізниці
"""

import time
import json
import csv
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore, Style
from tabulate import tabulate
import os
from dotenv import load_dotenv
from config import get_config, CSS_SELECTORS, POPULAR_ROUTES, FILTER_CONFIG

# Ініціалізація colorama для кольорового виводу
init(autoreset=True)

# Завантаження змінних середовища
load_dotenv()

@dataclass
class TicketInfo:
    """Інформація про квиток"""
    train_number: str
    departure_station: str
    arrival_station: str
    departure_time: str
    arrival_time: str
    travel_time: str
    price: str
    available_seats: str
    train_type: str
    date: str
    search_timestamp: str = None
    
    def __post_init__(self):
        if self.search_timestamp is None:
            self.search_timestamp = datetime.now().isoformat()

class UkrzaliznytsiaAgentV2:
    """Покращений агент для пошуку квитків на сайті Укрзалізниці"""
    
    def __init__(self, headless: bool = None, config: Dict = None):
        """
        Ініціалізація агента
        
        Args:
            headless: Запуск браузера в фоновому режимі
            config: Користувацька конфігурація
        """
        self.config = config or get_config()
        self.base_url = self.config["search"]["base_url"]
        self.css_selectors = self.config["css_selectors"]
        self.driver = None
        self.wait = None
        self.current_proxy = None
        self.request_count = 0
        self.last_request_time = time.time()
        
        # Використання користувацької конфігурації або значення за замовчуванням
        if headless is not None:
            self.config["browser"]["headless"] = headless
            
        self.setup_logging()
        self.setup_driver()
        
    def setup_logging(self):
        """Налаштування логування"""
        log_config = self.config["logging"]
        
        # Налаштування ротації логів
        from logging.handlers import RotatingFileHandler
        
        formatter = logging.Formatter(log_config["format"])
        
        # Файловий обробник з ротацією
        file_handler = RotatingFileHandler(
            log_config["file"],
            maxBytes=log_config["max_file_size"],
            backupCount=log_config["backup_count"],
            encoding=log_config["encoding"]
        )
        file_handler.setFormatter(formatter)
        
        # Консольний обробник
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Налаштування логера
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_config["level"]))
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def setup_driver(self):
        """Налаштування веб-драйвера"""
        try:
            browser_config = self.config["browser"]
            
            chrome_options = Options()
            if browser_config["headless"]:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"--window-size={browser_config['window_size']}")
            chrome_options.add_argument(f"--user-agent={browser_config['user_agent']}")
            
            # Додаткові опції для стабільності
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            
            # Налаштування проксі
            if self.config["proxy"]["use_proxy"] and self.config["proxy"]["proxy_list"]:
                self.current_proxy = self._get_next_proxy()
                if self.current_proxy:
                    chrome_options.add_argument(f"--proxy-server={self.current_proxy}")
            
            # Автоматичне завантаження ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Налаштування таймаутів
            self.driver.implicitly_wait(browser_config["implicit_wait"])
            self.driver.set_page_load_timeout(browser_config["page_load_timeout"])
            
            self.wait = WebDriverWait(self.driver, browser_config["timeout"])
            
            self.logger.info("Веб-драйвер успішно налаштовано")
            
        except Exception as e:
            self.logger.error(f"Помилка налаштування веб-драйвера: {e}")
            raise
            
    def _get_next_proxy(self) -> Optional[str]:
        """Отримання наступного проксі з списку"""
        if not self.config["proxy"]["proxy_list"]:
            return None
            
        if self.config["proxy"]["rotate_proxies"]:
            return random.choice(self.config["proxy"]["proxy_list"])
        else:
            # Проста ротація
            if not hasattr(self, '_proxy_index'):
                self._proxy_index = 0
            proxy = self.config["proxy"]["proxy_list"][self._proxy_index]
            self._proxy_index = (self._proxy_index + 1) % len(self.config["proxy"]["proxy_list"])
            return proxy
            
    def _rate_limit(self):
        """Обмеження частоти запитів"""
        if not self.config["security"]["rate_limiting"]:
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_request_time
        
        # Перевірка ліміту запитів на хвилину
        if self.request_count >= self.config["security"]["max_requests_per_minute"]:
            if time_diff < 60:
                sleep_time = 60 - time_diff
                self.logger.info(f"Досягнуто ліміт запитів. Очікую {sleep_time:.1f} секунд")
                time.sleep(sleep_time)
                self.request_count = 0
                self.last_request_time = time.time()
            else:
                self.request_count = 0
                self.last_request_time = current_time
                
        # Випадкова затримка
        if self.config["security"]["random_delays"]:
            delay = random.uniform(
                self.config["security"]["min_delay"],
                self.config["security"]["max_delay"]
            )
            time.sleep(delay)
            
    def open_website(self) -> bool:
        """Відкриття сайту Укрзалізниці"""
        try:
            self._rate_limit()
            self.request_count += 1
            
            self.logger.info("Відкриваю сайт Укрзалізниці...")
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Перевірка, чи сайт завантажився
            if "Укрзалізниця" in self.driver.title or "booking.uz.gov.ua" in self.driver.current_url:
                self.logger.info("Сайт успішно відкрито")
                return True
            else:
                self.logger.warning("Сайт може не завантажитися повністю")
                return False
                
        except Exception as e:
            self.logger.error(f"Помилка відкриття сайту: {e}")
            return False
            
    def search_tickets(self, from_station: str, to_station: str, date: str, 
                      retry_count: int = 0) -> List[TicketInfo]:
        """
        Пошук квитків з повторними спробами
        
        Args:
            from_station: Станція відправлення
            to_station: Станція призначення
            date: Дата поїздки (формат: DD.MM.YYYY)
            retry_count: Поточна кількість спроб
            
        Returns:
            Список знайдених квитків
        """
        try:
            self.logger.info(f"Шукаю квитки: {from_station} → {to_station} на {date}")
            
            # Заповнення форми пошуку
            if not self._fill_search_form(from_station, to_station, date):
                return []
                
            # Натискання кнопки пошуку
            if not self._click_search_button():
                return []
                
            # Очікування результатів
            if not self._wait_for_results():
                return []
                
            # Парсинг результатів
            tickets = self._parse_search_results()
            
            self.logger.info(f"Знайдено {len(tickets)} квитків")
            return tickets
            
        except Exception as e:
            self.logger.error(f"Помилка пошуку квитків: {e}")
            
            # Повторна спроба
            if retry_count < self.config["search"]["max_retries"]:
                self.logger.info(f"Повторна спроба {retry_count + 1}/{self.config['search']['max_retries']}")
                time.sleep(self.config["search"]["retry_delay"])
                return self.search_tickets(from_station, to_station, date, retry_count + 1)
            else:
                self.logger.error("Досягнуто максимальну кількість спроб")
                return []
                
    def _fill_search_form(self, from_station: str, to_station: str, date: str) -> bool:
        """Заповнення форми пошуку"""
        try:
            selectors = self.css_selectors["search_form"]
            
            # Поле "Звідки"
            from_field = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["from_station"]))
            )
            from_field.clear()
            from_field.send_keys(from_station)
            time.sleep(1)
            
            # Вибір першого результату з випадаючого списку
            try:
                first_option = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors["results"]["station_suggest"])
                first_option.click()
            except NoSuchElementException:
                self.logger.warning("Не вдалося знайти варіанти станцій для відправлення")
                
            # Поле "Куди"
            to_field = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["to_station"]))
            )
            to_field.clear()
            to_field.send_keys(to_station)
            time.sleep(1)
            
            # Вибір першого результату з випадаючого списку
            try:
                first_option = self.driver.find_element(By.CSS_SELECTOR, self.css_selectors["results"]["station_suggest"])
                first_option.click()
            except NoSuchElementException:
                self.logger.warning("Не вдалося знайти варіанти станцій для призначення")
                
            # Поле дати
            date_field = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["date"]))
            )
            date_field.clear()
            date_field.send_keys(date)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка заповнення форми: {e}")
            return False
            
    def _click_search_button(self) -> bool:
        """Натискання кнопки пошуку"""
        try:
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.css_selectors["search_form"]["search_button"]))
            )
            search_button.click()
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка натискання кнопки пошуку: {e}")
            return False
            
    def _wait_for_results(self) -> bool:
        """Очікування результатів пошуку"""
        try:
            # Очікуємо завантаження результатів
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.css_selectors["results"]["train_list"]))
            )
            time.sleep(3)  # Додатковий час для завантаження
            return True
            
        except TimeoutException:
            self.logger.warning("Таймаут очікування результатів")
            return False
        except Exception as e:
            self.logger.error(f"Помилка очікування результатів: {e}")
            return False
            
    def _parse_search_results(self) -> List[TicketInfo]:
        """Парсинг результатів пошуку"""
        tickets = []
        
        try:
            # Знаходимо всі поїзди
            train_elements = self.driver.find_elements(By.CSS_SELECTOR, self.css_selectors["results"]["train_item"])
            
            for train_element in train_elements:
                try:
                    ticket = self._parse_train_element(train_element)
                    if ticket:
                        tickets.append(ticket)
                except Exception as e:
                    self.logger.warning(f"Помилка парсингу поїзда: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Помилка парсингу результатів: {e}")
            
        return tickets
        
    def _parse_train_element(self, train_element) -> Optional[TicketInfo]:
        """Парсинг інформації про поїзд"""
        try:
            selectors = self.css_selectors["results"]
            
            # Отримання базової інформації про поїзд
            train_number = train_element.find_element(By.CSS_SELECTOR, selectors["train_number"]).text.strip()
            
            # Станції
            stations = train_element.find_elements(By.CSS_SELECTOR, selectors["station_name"])
            departure_station = stations[0].text.strip() if len(stations) > 0 else "Н/Д"
            arrival_station = stations[1].text.strip() if len(stations) > 1 else "Н/Д"
            
            # Час
            times = train_element.find_elements(By.CSS_SELECTOR, selectors["time"])
            departure_time = times[0].text.strip() if len(times) > 0 else "Н/Д"
            arrival_time = times[1].text.strip() if len(times) > 1 else "Н/Д"
            
            # Тривалість поїздки
            travel_time = train_element.find_element(By.CSS_SELECTOR, selectors["travel_time"]).text.strip()
            
            # Ціна
            price_element = train_element.find_element(By.CSS_SELECTOR, selectors["price"])
            price = price_element.text.strip()
            
            # Доступні місця
            seats_element = train_element.find_element(By.CSS_SELECTOR, selectors["seats"])
            available_seats = seats_element.text.strip()
            
            # Тип поїзда
            train_type = train_element.find_element(By.CSS_SELECTOR, selectors["train_type"]).text.strip()
            
            # Дата (беремо з поточного пошуку)
            date = datetime.now().strftime("%d.%m.%Y")
            
            return TicketInfo(
                train_number=train_number,
                departure_station=departure_station,
                arrival_station=arrival_station,
                departure_time=departure_time,
                arrival_time=arrival_time,
                travel_time=travel_time,
                price=price,
                available_seats=available_seats,
                train_type=train_type,
                date=date
            )
            
        except Exception as e:
            self.logger.warning(f"Помилка парсингу елемента поїзда: {e}")
            return None
            
    def search_multiple_routes(self, routes: List[Tuple[str, str]], date: str) -> Dict[str, List[TicketInfo]]:
        """
        Пошук квитків для кількох маршрутів
        
        Args:
            routes: Список кортежів (станція_відправлення, станція_призначення)
            date: Дата поїздки
            
        Returns:
            Словник з результатами пошуку для кожного маршруту
        """
        results = {}
        
        for from_station, to_station in routes:
            self.logger.info(f"Шукаю квитки для маршруту: {from_station} → {to_station}")
            
            tickets = self.search_tickets(from_station, to_station, date)
            results[f"{from_station}-{to_station}"] = tickets
            
            # Затримка між пошуками
            if from_station != routes[-1][0]:  # Не чекаємо після останнього пошуку
                time.sleep(self.config["search"]["delay_between_searches"])
                
        return results
        
    def search_date_range(self, from_station: str, to_station: str, 
                         start_date: datetime, end_date: datetime) -> List[TicketInfo]:
        """
        Пошук квитків для діапазону дат
        
        Args:
            from_station: Станція відправлення
            to_station: Станція призначення
            start_date: Початкова дата
            end_date: Кінцева дата
            
        Returns:
            Список всіх знайдених квитків
        """
        all_tickets = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%d.%m.%Y")
            self.logger.info(f"Шукаю квитки на {date_str}")
            
            tickets = self.search_tickets(from_station, to_station, date_str)
            
            if tickets:
                # Додаємо дату до кожного квитка
                for ticket in tickets:
                    ticket.date = date_str
                all_tickets.extend(tickets)
                self.logger.info(f"Знайдено {len(tickets)} квитків")
            else:
                self.logger.info("Квитки не знайдено")
                
            current_date += timedelta(days=1)
            
            # Затримка між пошуками
            if current_date <= end_date:
                time.sleep(self.config["search"]["delay_between_searches"])
                
        return all_tickets
        
    def filter_tickets(self, tickets: List[TicketInfo], **filters) -> List[TicketInfo]:
        """
        Фільтрація квитків за різними критеріями
        
        Args:
            tickets: Список квитків для фільтрації
            **filters: Критерії фільтрації
            
        Returns:
            Відфільтрований список квитків
        """
        filtered_tickets = tickets.copy()
        
        # Фільтрація за ціною
        if "max_price" in filters:
            max_price = filters["max_price"]
            filtered_tickets = [
                ticket for ticket in filtered_tickets
                if self._extract_price(ticket.price) <= max_price
            ]
            
        if "min_price" in filters:
            min_price = filters["min_price"]
            filtered_tickets = [
                ticket for ticket in filtered_tickets
                if self._extract_price(ticket.price) >= min_price
            ]
            
        # Фільтрація за часом відправлення
        if "departure_time_range" in filters:
            start_hour, end_hour = filters["departure_time_range"]
            filtered_tickets = [
                ticket for ticket in filtered_tickets
                if self._is_time_in_range(ticket.departure_time, start_hour, end_hour)
            ]
            
        # Фільтрація за типом поїзда
        if "train_types" in filters:
            allowed_types = filters["train_types"]
            filtered_tickets = [
                ticket for ticket in filtered_tickets
                if ticket.train_type in allowed_types
            ]
            
        return filtered_tickets
        
    def _extract_price(self, price_text: str) -> float:
        """Витягнення числового значення ціни"""
        try:
            # Видаляємо всі символи крім цифр та крапки
            price_clean = ''.join(c for c in price_text if c.isdigit() or c == '.')
            return float(price_clean) if price_clean else float('inf')
        except:
            return float('inf')
            
    def _is_time_in_range(self, time_text: str, start_hour: int, end_hour: int) -> bool:
        """Перевірка, чи час знаходиться в діапазоні"""
        try:
            hour = int(time_text.split(':')[0])
            
            if start_hour <= end_hour:
                return start_hour <= hour <= end_hour
            else:  # Для нічних поїздів (наприклад, 22:00 - 06:00)
                return hour >= start_hour or hour <= end_hour
        except:
            return False
            
    def display_tickets(self, tickets: List[TicketInfo], format_type: str = "table"):
        """
        Відображення знайдених квитків
        
        Args:
            tickets: Список квитків
            format_type: Тип форматування (table, list, summary)
        """
        if not tickets:
            print(f"{Fore.YELLOW}Квитки не знайдено{Style.RESET_ALL}")
            return
            
        if format_type == "table":
            self._display_table(tickets)
        elif format_type == "list":
            self._display_list(tickets)
        elif format_type == "summary":
            self._display_summary(tickets)
        else:
            self._display_table(tickets)
            
    def _display_table(self, tickets: List[TicketInfo]):
        """Відображення квитків у таблиці"""
        # Підготовка даних для таблиці
        table_data = []
        for i, ticket in enumerate(tickets, 1):
            table_data.append([
                i,
                ticket.train_number,
                f"{ticket.departure_station} → {ticket.arrival_station}",
                f"{ticket.departure_time} - {ticket.arrival_time}",
                ticket.travel_time,
                ticket.price,
                ticket.available_seats,
                ticket.train_type
            ])
            
        # Заголовки таблиці
        headers = [
            "№", "Номер поїзда", "Маршрут", "Час", 
            "Тривалість", "Ціна", "Місця", "Тип"
        ]
        
        # Виведення таблиці
        print(f"\n{Fore.CYAN}Знайдені квитки:{Style.RESET_ALL}")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
    def _display_list(self, tickets: List[TicketInfo]):
        """Відображення квитків у списку"""
        print(f"\n{Fore.CYAN}Знайдені квитки:{Style.RESET_ALL}")
        
        for i, ticket in enumerate(tickets, 1):
            print(f"\n{Fore.GREEN}{i}. Поїзд {ticket.train_number} ({ticket.train_type}){Style.RESET_ALL}")
            print(f"   Маршрут: {ticket.departure_station} → {ticket.arrival_station}")
            print(f"   Час: {ticket.departure_time} - {ticket.arrival_time} ({ticket.travel_time})")
            print(f"   Ціна: {ticket.price}, Місця: {ticket.available_seats}")
            
    def _display_summary(self, tickets: List[TicketInfo]):
        """Відображення зведення по квитках"""
        if not tickets:
            return
            
        print(f"\n{Fore.CYAN}Зведення пошуку:{Style.RESET_ALL}")
        print(f"Всього знайдено: {len(tickets)} квитків")
        
        # Статистика за типами поїздів
        train_types = {}
        for ticket in tickets:
            train_types[ticket.train_type] = train_types.get(ticket.train_type, 0) + 1
            
        print(f"\n{Fore.YELLOW}За типами поїздів:{Style.RESET_ALL}")
        for train_type, count in train_types.items():
            print(f"  {train_type}: {count}")
            
        # Статистика за цінами
        prices = [self._extract_price(ticket.price) for ticket in tickets if self._extract_price(ticket.price) != float('inf')]
        if prices:
            print(f"\n{Fore.YELLOW}За цінами:{Style.RESET_ALL}")
            print(f"  Мінімальна: {min(prices):.2f} грн")
            print(f"  Максимальна: {max(prices):.2f} грн")
            print(f"  Середня: {sum(prices)/len(prices):.2f} грн")
            
    def save_tickets(self, tickets: List[TicketInfo], filename: str = None, 
                    format_type: str = None) -> str:
        """
        Збереження квитків у файл
        
        Args:
            tickets: Список квитків для збереження
            filename: Назва файлу
            format_type: Тип файлу (json, csv, txt)
            
        Returns:
            Назва збереженого файлу
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            format_type = format_type or self.config["save"]["default_format"]
            filename = f"tickets_{timestamp}.{format_type}"
            
        if not format_type:
            format_type = filename.split('.')[-1] if '.' in filename else self.config["save"]["default_format"]
            
        try:
            if format_type.lower() == "json":
                self._save_as_json(tickets, filename)
            elif format_type.lower() == "csv":
                self._save_as_csv(tickets, filename)
            elif format_type.lower() == "txt":
                self._save_as_txt(tickets, filename)
            else:
                raise ValueError(f"Непідтримуваний формат файлу: {format_type}")
                
            self.logger.info(f"Квитки збережено у файл: {filename}")
            print(f"{Fore.GREEN}Квитки збережено у файл: {filename}{Style.RESET_ALL}")
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Помилка збереження файлу: {e}")
            print(f"{Fore.RED}Помилка збереження файлу: {e}{Style.RESET_ALL}")
            raise
            
    def _save_as_json(self, tickets: List[TicketInfo], filename: str):
        """Збереження у JSON форматі"""
        tickets_data = []
        for ticket in tickets:
            ticket_dict = asdict(ticket)
            tickets_data.append(ticket_dict)
            
        # Додавання метаданих
        if self.config["save"]["include_metadata"]:
            metadata = {
                "search_info": {
                    "timestamp": datetime.now().isoformat(),
                    "total_tickets": len(tickets),
                    "agent_version": "2.0"
                },
                "tickets": tickets_data
            }
            data_to_save = metadata
        else:
            data_to_save = tickets_data
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            
    def _save_as_csv(self, tickets: List[TicketInfo], filename: str):
        """Збереження у CSV форматі"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if tickets:
                fieldnames = list(asdict(tickets[0]).keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for ticket in tickets:
                    writer.writerow(asdict(ticket))
                    
    def _save_as_txt(self, tickets: List[TicketInfo], filename: str):
        """Збереження у текстовому форматі"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Результати пошуку квитків\n")
            f.write(f"Дата пошуку: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"Всього знайдено: {len(tickets)} квитків\n\n")
            
            for i, ticket in enumerate(tickets, 1):
                f.write(f"{i}. Поїзд {ticket.train_number} ({ticket.train_type})\n")
                f.write(f"   Маршрут: {ticket.departure_station} → {ticket.arrival_station}\n")
                f.write(f"   Час: {ticket.departure_time} - {ticket.arrival_time} ({ticket.travel_time})\n")
                f.write(f"   Ціна: {ticket.price}, Місця: {ticket.available_seats}\n")
                f.write(f"   Дата: {ticket.date}\n\n")
                
    def get_popular_routes(self) -> List[Tuple[str, str]]:
        """Отримання списку популярних маршрутів"""
        return POPULAR_ROUTES.copy()
        
    def get_filter_config(self) -> Dict:
        """Отримання конфігурації фільтрів"""
        return FILTER_CONFIG.copy()
        
    def close(self):
        """Закриття браузера та очищення ресурсів"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Браузер закрито")
            except Exception as e:
                self.logger.error(f"Помилка закриття браузера: {e}")
                
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Головна функція для демонстрації роботи агента"""
    print(f"{Fore.CYAN}=== Покращений агент пошуку квитків Укрзалізниці ==={Style.RESET_ALL}")
    
    try:
        with UkrzaliznytsiaAgentV2(headless=False) as agent:
            # Відкриття сайту
            if not agent.open_website():
                print(f"{Fore.RED}Не вдалося відкрити сайт{Style.RESET_ALL}")
                return
                
            # Пошук квитків (приклад)
            from_station = "Київ"
            to_station = "Львів"
            date = (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")
            
            print(f"\n{Fore.YELLOW}Шукаю квитки: {from_station} → {to_station} на {date}{Style.RESET_ALL}")
            
            tickets = agent.search_tickets(from_station, to_station, date)
            
            if tickets:
                # Відображення результатів
                agent.display_tickets(tickets, "table")
                
                # Фільтрація за ціною
                affordable_tickets = agent.filter_tickets(tickets, max_price=1000)
                if affordable_tickets:
                    print(f"\n{Fore.GREEN}Квитки дешевше 1000 грн:{Style.RESET_ALL}")
                    agent.display_tickets(affordable_tickets, "summary")
                
                # Збереження у різних форматах
                agent.save_tickets(tickets, format_type="json")
                agent.save_tickets(tickets, format_type="csv")
            else:
                print(f"{Fore.YELLOW}Квитки не знайдено{Style.RESET_ALL}")
                
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Пошук перервано користувачем{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Помилка: {e}{Style.RESET_ALL}")
        logging.error(f"Критична помилка: {e}")


if __name__ == "__main__":
    main()