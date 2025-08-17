#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрація агента пошуку квитків Укрзалізниці
(без встановлених залежностей)
"""

import os
import sys
from datetime import datetime, timedelta

def print_header():
    """Виведення заголовка"""
    print("=" * 70)
    print("🚂 АГЕНТ ПОШУКУ КВИТКІВ УКРЗАЛІЗНИЦІ")
    print("=" * 70)
    print("Автоматизований пошук та аналіз квитків на поїзди")
    print("=" * 70)

def check_dependencies():
    """Перевірка залежностей"""
    print("📦 Перевірка залежностей...")
    
    dependencies = {
        "selenium": "Автоматизація браузера",
        "webdriver-manager": "Управління ChromeDriver",
        "requests": "HTTP запити",
        "beautifulsoup4": "Парсинг HTML",
        "colorama": "Кольоровий вивід",
        "tabulate": "Форматування таблиць"
    }
    
    missing = []
    available = []
    
    for dep, description in dependencies.items():
        try:
            __import__(dep.replace("-", "_"))
            print(f"✅ {dep:<20} - {description}")
            available.append(dep)
        except ImportError:
            print(f"❌ {dep:<20} - {description}")
            missing.append(dep)
    
    print()
    return available, missing

def show_project_structure():
    """Показ структури проекту"""
    print("📁 Структура проекту:")
    print("├── ukrzaliznytsia_agent.py          # Базова версія агента")
    print("├── ukrzaliznytsia_agent_v2.py       # Покращена версія з конфігурацією")
    print("├── config.py                         # Файл конфігурації")
    print("├── example_usage.py                  # Приклади використання")
    print("├── quick_test.py                     # Швидкий тест")
    print("├── requirements.txt                  # Залежності Python")
    print("├── install.sh                        # Скрипт встановлення (Linux/Mac)")
    print("├── install.bat                       # Скрипт встановлення (Windows)")
    print("├── README.md                         # Документація")
    print("└── LICENSE                           # Ліцензія MIT")
    print()

def show_features():
    """Показ особливостей агента"""
    print("🌟 Особливості агента:")
    print("• Автоматизований пошук квитків за маршрутом та датою")
    print("• Підтримка множинних маршрутів та діапазонів дат")
    print("• Розширена фільтрація за ціною, часом, типом поїзда")
    print("• Збереження результатів у різних форматах (JSON, CSV, TXT)")
    print("• Налаштовувана конфігурація та логування")
    print("• Обмеження частоти запитів для безпечного використання")
    print("• Підтримка проксі та ротація IP-адрес")
    print("• Кольоровий вивід та зручні таблиці результатів")
    print()

def show_usage_examples():
    """Показ прикладів використання"""
    print("💻 Приклади використання:")
    
    print("1. Базовий пошук:")
    print("   from ukrzaliznytsia_agent_v2 import UkrzaliznytsiaAgentV2")
    print("   with UkrzaliznytsiaAgentV2() as agent:")
    print("       tickets = agent.search_tickets('Київ', 'Львів', '25.12.2024')")
    print()
    
    print("2. Пошук для кількох маршрутів:")
    print("   routes = [('Київ', 'Харків'), ('Київ', 'Одеса')]")
    print("   results = agent.search_multiple_routes(routes, '25.12.2024')")
    print()
    
    print("3. Фільтрація результатів:")
    print("   affordable = agent.filter_tickets(tickets, max_price=1000)")
    print("   morning = agent.filter_tickets(tickets, departure_time_range=(6, 12))")
    print()
    
    print("4. Збереження результатів:")
    print("   agent.save_tickets(tickets, format_type='json')")
    print("   agent.save_tickets(tickets, format_type='csv')")
    print()

def show_installation_instructions():
    """Показ інструкцій по встановленню"""
    print("🚀 Інструкції по встановленню:")
    
    if os.name == 'nt':  # Windows
        print("Windows:")
        print("   install.bat")
        print("   або")
        print("   python -m venv venv")
        print("   venv\\Scripts\\activate.bat")
        print("   pip install -r requirements.txt")
    else:  # Linux/Mac
        print("Linux/Mac:")
        print("   ./install.sh")
        print("   або")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
    
    print()
    print("Після встановлення:")
    print("   python quick_test.py          # Швидкий тест")
    print("   python example_usage.py       # Приклади використання")
    print("   python ukrzaliznytsia_agent_v2.py  # Основний агент")
    print()

def show_configuration():
    """Показ конфігурації"""
    print("⚙️  Налаштування конфігурації:")
    
    try:
        from config import get_config
        
        config = get_config()
        print(f"• Браузер: {len(config['browser'])} параметрів")
        print(f"• Пошук: {len(config['search'])} параметрів")
        print(f"• Безпека: {len(config['security'])} параметрів")
        print(f"• Фільтри: {len(config['filters'])} категорій")
        print(f"• Популярні маршрути: {len(config['popular_routes'])} маршрутів")
        
        # Показ популярних маршрутів
        print("\nПопулярні маршрути:")
        for i, (from_st, to_st) in enumerate(config['popular_routes'][:5], 1):
            print(f"  {i}. {from_st} → {to_st}")
        if len(config['popular_routes']) > 5:
            print(f"  ... та ще {len(config['popular_routes']) - 5} маршрутів")
            
    except ImportError:
        print("❌ Конфігурація недоступна (залежності не встановлено)")
    
    print()

def show_safety_features():
    """Показ функцій безпеки"""
    print("🔒 Функції безпеки:")
    print("• Обмеження частоти запитів (за замовчуванням: 30 запитів/хв)")
    print("• Випадкові затримки між запитами")
    print("• Повага до robots.txt")
    print("• Автоматичне закриття браузера")
    print("• Логування всіх дій")
    print("• Обробка помилок та повторні спроби")
    print()

def show_roadmap():
    """Показ плану розвитку"""
    print("🗺️  План розвитку:")
    print("• Підтримка інших браузерів (Firefox, Edge)")
    print("• Веб-інтерфейс для агента")
    print("• Telegram бот для сповіщень")
    print("• База даних для збереження історії пошуків")
    print("• Аналітика та статистика квитків")
    print("• Інтеграція з іншими транспортними системами")
    print()

def main():
    """Головна функція"""
    print_header()
    
    # Перевірка залежностей
    available, missing = check_dependencies()
    
    if missing:
        print(f"⚠️  Відсутні залежності: {len(missing)}")
        print("Для повноцінної роботи потрібно встановити всі залежності.")
        print()
    else:
        print("✅ Всі залежності доступні!")
        print()
    
    # Показ інформації про проект
    show_project_structure()
    show_features()
    show_usage_examples()
    show_configuration()
    show_safety_features()
    show_roadmap()
    
    # Інструкції по встановленню
    if missing:
        show_installation_instructions()
    
    print("=" * 70)
    print("🎯 Агент готовий до використання!")
    
    if missing:
        print("📥 Спочатку встановіть залежності за допомогою скриптів встановлення.")
    
    print("📚 Детальна документація: README.md")
    print("🧪 Тестування: python quick_test.py")
    print("💡 Приклади: python example_usage.py")
    print("=" * 70)

if __name__ == "__main__":
    main()