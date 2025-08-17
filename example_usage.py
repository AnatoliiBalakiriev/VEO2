#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Приклади використання агента пошуку квитків Укрзалізниці
"""

from datetime import datetime, timedelta
from ukrzaliznytsia_agent import UkrzaliznytsiaAgent, TicketInfo
import time

def example_basic_search():
    """Базовий приклад пошуку квитків"""
    print("=== Базовий пошук квитків ===")
    
    with UkrzaliznytsiaAgent(headless=False) as agent:
        # Відкриття сайту
        if not agent.open_website():
            print("Не вдалося відкрити сайт")
            return
            
        # Пошук квитків
        from_station = "Київ"
        to_station = "Львів"
        date = (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")
        
        print(f"Шукаю квитки: {from_station} → {to_station} на {date}")
        
        tickets = agent.search_tickets(from_station, to_station, date)
        
        if tickets:
            agent.display_tickets(tickets)
            agent.save_tickets_to_file(tickets, "basic_search_results.json")
        else:
            print("Квитки не знайдено")

def example_multiple_routes():
    """Приклад пошуку квитків для кількох маршрутів"""
    print("\n=== Пошук для кількох маршрутів ===")
    
    routes = [
        ("Київ", "Харків"),
        ("Київ", "Одеса"),
        ("Львів", "Київ"),
        ("Дніпро", "Київ")
    ]
    
    date = (datetime.now() + timedelta(days=14)).strftime("%d.%m.%Y")
    
    with UkrzaliznytsiaAgent(headless=False) as agent:
        if not agent.open_website():
            print("Не вдалося відкрити сайт")
            return
            
        all_tickets = {}
        
        for from_station, to_station in routes:
            print(f"\nШукаю квитки: {from_station} → {to_station}")
            
            tickets = agent.search_tickets(from_station, to_station, date)
            all_tickets[f"{from_station}-{to_station}"] = tickets
            
            # Пауза між пошуками
            time.sleep(2)
            
        # Виведення всіх результатів
        for route, tickets in all_tickets.items():
            print(f"\n--- Маршрут: {route} ---")
            if tickets:
                agent.display_tickets(tickets)
            else:
                print("Квитки не знайдено")
                
        # Збереження всіх результатів
        agent.save_tickets_to_file(
            [ticket for tickets in all_tickets.values() for ticket in tickets],
            f"multiple_routes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

def example_date_range_search():
    """Приклад пошуку квитків для діапазону дат"""
    print("\n=== Пошук для діапазону дат ===")
    
    from_station = "Київ"
    to_station = "Львів"
    
    # Пошук на наступні 30 днів
    start_date = datetime.now() + timedelta(days=1)
    end_date = datetime.now() + timedelta(days=30)
    
    with UkrzaliznytsiaAgent(headless=False) as agent:
        if not agent.open_website():
            print("Не вдалося відкрити сайт")
            return
            
        all_tickets = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%d.%m.%Y")
            print(f"Шукаю квитки на {date_str}")
            
            tickets = agent.search_tickets(from_station, to_station, date_str)
            
            if tickets:
                # Додаємо дату до кожного квитка
                for ticket in tickets:
                    ticket.date = date_str
                all_tickets.extend(tickets)
                print(f"Знайдено {len(tickets)} квитків")
            else:
                print("Квитки не знайдено")
                
            current_date += timedelta(days=1)
            time.sleep(3)  # Пауза між пошуками
            
        if all_tickets:
            print(f"\nВсього знайдено {len(all_tickets)} квитків")
            agent.display_tickets(all_tickets)
            agent.save_tickets_to_file(all_tickets, f"date_range_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json")
        else:
            print("Квитки не знайдено для жодної дати")

def example_filtered_search():
    """Приклад пошуку з фільтрацією результатів"""
    print("\n=== Пошук з фільтрацією ===")
    
    with UkrzaliznytsiaAgent(headless=False) as agent:
        if not agent.open_website():
            print("Не вдалося відкрити сайту")
            return
            
        from_station = "Київ"
        to_station = "Одеса"
        date = (datetime.now() + timedelta(days=10)).strftime("%d.%m.%Y")
        
        tickets = agent.search_tickets(from_station, to_station, date)
        
        if tickets:
            print(f"Знайдено {len(tickets)} квитків")
            
            # Фільтрація за ціною (приблизно)
            affordable_tickets = []
            for ticket in tickets:
                try:
                    # Спроба витягти числове значення ціни
                    price_text = ticket.price.replace('грн', '').replace(' ', '').strip()
                    if price_text.isdigit():
                        price = int(price_text)
                        if price < 1000:  # Квитки дешевше 1000 грн
                            affordable_tickets.append(ticket)
                except:
                    continue
                    
            print(f"Квитки дешевше 1000 грн: {len(affordable_tickets)}")
            
            if affordable_tickets:
                agent.display_tickets(affordable_tickets)
                agent.save_tickets_to_file(affordable_tickets, "affordable_tickets.json")
                
            # Фільтрація за часом відправлення (ранкові поїзди)
            morning_tickets = []
            for ticket in tickets:
                try:
                    departure_hour = int(ticket.departure_time.split(':')[0])
                    if 6 <= departure_hour <= 12:  # Поїзди з 6:00 до 12:00
                        morning_tickets.append(ticket)
                except:
                    continue
                    
            print(f"Ранкові поїзди (6:00-12:00): {len(morning_tickets)}")
            
            if morning_tickets:
                agent.display_tickets(morning_tickets)
                agent.save_tickets_to_file(morning_tickets, "morning_tickets.json")
        else:
            print("Квитки не знайдено")

def interactive_search():
    """Інтерактивний пошук квитків"""
    print("\n=== Інтерактивний пошук ===")
    
    print("Введіть параметри пошуку:")
    from_station = input("Станція відправлення: ").strip()
    to_station = input("Станція призначення: ").strip()
    
    # Запит дати
    while True:
        date_input = input("Дата поїздки (DD.MM.YYYY або 'завтра', 'післязавтра'): ").strip()
        
        if date_input.lower() == 'завтра':
            date = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
            break
        elif date_input.lower() == 'післязавтра':
            date = (datetime.now() + timedelta(days=2)).strftime("%d.%m.%Y")
            break
        elif len(date_input) == 10 and date_input[2] == '.' and date_input[5] == '.':
            date = date_input
            break
        else:
            print("Невірний формат дати. Спробуйте ще раз.")
    
    print(f"\nШукаю квитки: {from_station} → {to_station} на {date}")
    
    with UkrzaliznytsiaAgent(headless=False) as agent:
        if not agent.open_website():
            print("Не вдалося відкрити сайт")
            return
            
        tickets = agent.search_tickets(from_station, to_station, date)
        
        if tickets:
            agent.display_tickets(tickets)
            
            # Запит на збереження
            save_choice = input("\nЗберегти результати у файл? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes', 'так', 'т']:
                filename = input("Назва файлу (Enter для автоматичної): ").strip()
                if not filename:
                    filename = None
                agent.save_tickets_to_file(tickets, filename)
        else:
            print("Квитки не знайдено")

def main():
    """Головна функція з меню вибору"""
    print("=== Агент пошуку квитків Укрзалізниці - Приклади використання ===\n")
    
    examples = {
        "1": ("Базовий пошук квитків", example_basic_search),
        "2": ("Пошук для кількох маршрутів", example_multiple_routes),
        "3": ("Пошук для діапазону дат", example_date_range_search),
        "4": ("Пошук з фільтрацією", example_filtered_search),
        "5": ("Інтерактивний пошук", interactive_search),
        "0": ("Вихід", None)
    }
    
    while True:
        print("\nВиберіть приклад:")
        for key, (description, _) in examples.items():
            if key != "0":
                print(f"{key}. {description}")
            else:
                print(f"{key}. {description}")
        
        choice = input("\nВаш вибір: ").strip()
        
        if choice == "0":
            print("До побачення!")
            break
        elif choice in examples:
            try:
                examples[choice][1]()
            except KeyboardInterrupt:
                print("\nПошук перервано користувачем")
            except Exception as e:
                print(f"Помилка: {e}")
        else:
            print("Невірний вибір. Спробуйте ще раз.")

if __name__ == "__main__":
    main()