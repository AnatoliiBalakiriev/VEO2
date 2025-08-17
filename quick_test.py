#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Швидкий тест агента пошуку квитків Укрзалізниці
"""

import sys
import os
from datetime import datetime, timedelta

# Додаємо поточну директорію до шляху Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ukrzaliznytsia_agent_v2 import UkrzaliznytsiaAgentV2
    print("✅ Агент успішно імпортовано")
except ImportError as e:
    print(f"❌ Помилка імпорту агента: {e}")
    print("Переконайтеся, що всі залежності встановлено:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def quick_test():
    """Швидкий тест основного функціоналу"""
    print("🚂 Запуск швидкого тесту агента пошуку квитків...")
    
    try:
        # Створення агента
        print("📱 Створюю агента...")
        agent = UkrzaliznytsiaAgentV2(headless=True)  # Фоновий режим для тесту
        
        # Тест відкриття сайту
        print("🌐 Відкриваю сайт Укрзалізниці...")
        if agent.open_website():
            print("✅ Сайт успішно відкрито")
        else:
            print("❌ Не вдалося відкрити сайт")
            return False
            
        # Тест пошуку квитків
        print("🔍 Тестую пошук квитків...")
        from_station = "Київ"
        to_station = "Львів"
        date = (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")
        
        print(f"   Маршрут: {from_station} → {to_station}")
        print(f"   Дата: {date}")
        
        tickets = agent.search_tickets(from_station, to_station, date)
        
        if tickets:
            print(f"✅ Знайдено {len(tickets)} квитків")
            
            # Тест фільтрації
            print("🔧 Тестую фільтрацію...")
            affordable_tickets = agent.filter_tickets(tickets, max_price=1000)
            print(f"   Квитки дешевше 1000 грн: {len(affordable_tickets)}")
            
            # Тест збереження
            print("💾 Тестую збереження...")
            filename = agent.save_tickets(tickets, format_type="json")
            print(f"   Збережено у файл: {filename}")
            
            # Тест відображення
            print("📊 Тестую відображення...")
            agent.display_tickets(tickets, "summary")
            
        else:
            print("⚠️  Квитки не знайдено (це може бути нормально)")
            
        # Тест конфігурації
        print("⚙️  Тестую конфігурацію...")
        popular_routes = agent.get_popular_routes()
        print(f"   Популярні маршрути: {len(popular_routes)}")
        
        filter_config = agent.get_filter_config()
        print(f"   Налаштування фільтрів: {len(filter_config)} категорій")
        
        print("✅ Всі тести пройдено успішно!")
        return True
        
    except Exception as e:
        print(f"❌ Помилка під час тестування: {e}")
        return False
        
    finally:
        # Закриття агента
        if 'agent' in locals():
            agent.close()
            print("🔒 Агент закрито")

def test_config():
    """Тест конфігурації"""
    print("\n⚙️  Тест конфігурації...")
    
    try:
        from config import get_config, validate_config
        
        config = get_config()
        print(f"✅ Конфігурація завантажена: {len(config)} секцій")
        
        errors = validate_config()
        if errors:
            print("❌ Помилки в конфігурації:")
            for error in errors:
                print(f"   - {error}")
            return False
        else:
            print("✅ Конфігурація валідна")
            return True
            
    except Exception as e:
        print(f"❌ Помилка тестування конфігурації: {e}")
        return False

def test_dependencies():
    """Тест залежностей"""
    print("\n📦 Тест залежностей...")
    
    dependencies = [
        "selenium",
        "webdriver-manager", 
        "requests",
        "beautifulsoup4",
        "colorama",
        "tabulate"
    ]
    
    all_ok = True
    
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - не встановлено")
            all_ok = False
            
    return all_ok

def main():
    """Головна функція тестування"""
    print("=" * 60)
    print("🚂 ШВИДКИЙ ТЕСТ АГЕНТА ПОШУКУ КВИТКІВ УКРЗАЛІЗНИЦІ")
    print("=" * 60)
    
    # Тест залежностей
    deps_ok = test_dependencies()
    
    # Тест конфігурації
    config_ok = test_config()
    
    # Тест основного функціоналу
    if deps_ok and config_ok:
        print("\n" + "=" * 60)
        print("🚀 ЗАПУСК ОСНОВНОГО ТЕСТУ")
        print("=" * 60)
        
        main_test_ok = quick_test()
        
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТИ ТЕСТУВАННЯ")
        print("=" * 60)
        
        print(f"📦 Залежності: {'✅' if deps_ok else '❌'}")
        print(f"⚙️  Конфігурація: {'✅' if config_ok else '❌'}")
        print(f"🚀 Основний функціонал: {'✅' if main_test_ok else '❌'}")
        
        if deps_ok and config_ok and main_test_ok:
            print("\n🎉 Всі тести пройдено успішно! Агент готовий до роботи.")
        else:
            print("\n⚠️  Деякі тести не пройдено. Перевірте налаштування.")
            
    else:
        print("\n❌ Тестування основного функціоналу пропущено через помилки")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()