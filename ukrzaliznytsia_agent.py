#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Агент для пошуку квитків на сайті Укрзалізниці
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore, Style
from tabulate import tabulate
import os
from dotenv import load_dotenv

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

class UkrzaliznytsiaAgent:
    """Агент для пошуку квитків на сайті Укрзалізниці"""
    
    def __init__(self, headless: bool = False):
        """
        Ініціалізація агента
        
        Args:
            headless: Запуск браузера в фоновому режимі
        """
        self.base_url = "https://booking.uz.gov.ua/"
        self.driver = None
        self.wait = None
        self.setup_logging()
        self.setup_driver(headless)
        
    def setup_logging(self):
        """Налаштування логування"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ukrzaliznytsia.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self, headless: bool):
        """Налаштування веб-драйвера"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Автоматичне завантаження ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            self.logger.info("Веб-драйвер успішно налаштовано")
            
        except Exception as e:
            self.logger.error(f"Помилка налаштування веб-драйвера: {e}")
            raise
            
    def open_website(self):
        """Відкриття сайту Укрзалізниці"""
        try:
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
            
    def search_tickets(self, from_station: str, to_station: str, date: str) -> List[TicketInfo]:
        """
        Пошук квитків
        
        Args:
            from_station: Станція відправлення
            to_station: Станція призначення
            date: Дата поїздки (формат: DD.MM.YYYY)
            
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
            return []
            
    def _fill_search_form(self, from_station: str, to_station: str, date: str) -> bool:
        """Заповнення форми пошуку"""
        try:
            # Поле "Звідки"
            from_field = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Звідки']"))
            )
            from_field.clear()
            from_field.send_keys(from_station)
            time.sleep(1)
            
            # Вибір першого результату з випадаючого списку
            try:
                first_option = self.driver.find_element(By.CSS_SELECTOR, ".station-suggest-item")
                first_option.click()
            except NoSuchElementException:
                self.logger.warning("Не вдалося знайти варіанти станцій для відправлення")
                
            # Поле "Куди"
            to_field = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Куди']"))
            )
            to_field.clear()
            to_field.send_keys(to_station)
            time.sleep(1)
            
            # Вибір першого результату з випадаючого списку
            try:
                first_option = self.driver.find_element(By.CSS_SELECTOR, ".station-suggest-item")
                first_option.click()
            except NoSuchElementException:
                self.logger.warning("Не вдалося знайти варіанти станцій для призначення")
                
            # Поле дати
            date_field = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='date']"))
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
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
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
                EC.presence_of_element_located((By.CSS_SELECTOR, ".train-list"))
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
            train_elements = self.driver.find_elements(By.CSS_SELECTOR, ".train-item")
            
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
            # Отримання базової інформації про поїзд
            train_number = train_element.find_element(By.CSS_SELECTOR, ".train-number").text.strip()
            
            # Станції
            stations = train_element.find_elements(By.CSS_SELECTOR, ".station-name")
            departure_station = stations[0].text.strip() if len(stations) > 0 else "Н/Д"
            arrival_station = stations[1].text.strip() if len(stations) > 1 else "Н/Д"
            
            # Час
            times = train_element.find_elements(By.CSS_SELECTOR, ".time")
            departure_time = times[0].text.strip() if len(times) > 0 else "Н/Д"
            arrival_time = times[1].text.strip() if len(times) > 1 else "Н/Д"
            
            # Тривалість поїздки
            travel_time = train_element.find_element(By.CSS_SELECTOR, ".travel-time").text.strip()
            
            # Ціна
            price_element = train_element.find_element(By.CSS_SELECTOR, ".price")
            price = price_element.text.strip()
            
            # Доступні місця
            seats_element = train_element.find_element(By.CSS_SELECTOR, ".seats")
            available_seats = seats_element.text.strip()
            
            # Тип поїзда
            train_type = train_element.find_element(By.CSS_SELECTOR, ".train-type").text.strip()
            
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
            
    def display_tickets(self, tickets: List[TicketInfo]):
        """Відображення знайдених квитків у таблиці"""
        if not tickets:
            print(f"{Fore.YELLOW}Квитки не знайдено{Style.RESET_ALL}")
            return
            
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
        
    def save_tickets_to_file(self, tickets: List[TicketInfo], filename: str = None):
        """Збереження квитків у файл"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tickets_{timestamp}.json"
            
        try:
            # Конвертація в словники для JSON
            tickets_data = []
            for ticket in tickets:
                tickets_data.append({
                    "train_number": ticket.train_number,
                    "departure_station": ticket.departure_station,
                    "arrival_station": ticket.arrival_station,
                    "departure_time": ticket.departure_time,
                    "arrival_time": ticket.arrival_time,
                    "travel_time": ticket.travel_time,
                    "price": ticket.price,
                    "available_seats": ticket.available_seats,
                    "train_type": ticket.train_type,
                    "date": ticket.date
                })
                
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tickets_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Квитки збережено у файл: {filename}")
            print(f"{Fore.GREEN}Квитки збережено у файл: {filename}{Style.RESET_ALL}")
            
        except Exception as e:
            self.logger.error(f"Помилка збереження файлу: {e}")
            print(f"{Fore.RED}Помилка збереження файлу: {e}{Style.RESET_ALL}")
            
    def close(self):
        """Закриття браузера та очищення ресурсів"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Браузер закрито")
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Головна функція для демонстрації роботи агента"""
    print(f"{Fore.CYAN}=== Агент пошуку квитків Укрзалізниці ==={Style.RESET_ALL}")
    
    # Приклад використання
    try:
        with UkrzaliznytsiaAgent(headless=False) as agent:
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
                agent.display_tickets(tickets)
                
                # Збереження у файл
                agent.save_tickets_to_file(tickets)
            else:
                print(f"{Fore.YELLOW}Квитки не знайдено{Style.RESET_ALL}")
                
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Пошук перервано користувачем{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Помилка: {e}{Style.RESET_ALL}")
        logging.error(f"Критична помилка: {e}")


if __name__ == "__main__":
    main()