#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Перевірка системи та Python для агента пошуку квитків Укрзалізниці
"""

import sys
import platform
import os
from datetime import datetime

def check_python_version():
    """Перевірка версії Python"""
    print("🐍 Перевірка версії Python...")
    
    version = sys.version_info
    print(f"   Версія: {version.major}.{version.minor}.{version.micro}")
    print(f"   Реліз: {version.releaselevel}")
    
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Версія Python відповідає вимогам (3.8+)")
        return True
    else:
        print("   ❌ Версія Python занадто стара. Потрібна версія 3.8+")
        return False

def check_platform():
    """Перевірка платформи"""
    print("\n🖥️  Інформація про систему...")
    
    print(f"   Операційна система: {platform.system()}")
    print(f"   Версія ОС: {platform.release()}")
    print(f"   Архітектура: {platform.machine()}")
    print(f"   Процесор: {platform.processor()}")
    
    if platform.system() == "Windows":
        print("   💡 Для Windows використовуйте: install.bat")
    else:
        print("   💡 Для Linux/Mac використовуйте: ./install.sh")

def check_pip():
    """Перевірка pip"""
    print("\n📦 Перевірка pip...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ pip знайдено: {result.stdout.strip()}")
            return True
        else:
            print("   ❌ pip не працює")
            return False
    except Exception as e:
        print(f"   ❌ Помилка перевірки pip: {e}")
        return False

def check_virtual_env():
    """Перевірка віртуального середовища"""
    print("\n🔧 Перевірка віртуального середовища...")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ Віртуальне середовище активовано")
        print(f"   Шлях: {sys.prefix}")
        return True
    else:
        print("   ⚠️  Віртуальне середовище не активовано")
        print("   💡 Рекомендується створити віртуальне середовище")
        return False

def check_dependencies():
    """Перевірка залежностей"""
    print("\n📚 Перевірка залежностей...")
    
    dependencies = {
        "selenium": "Автоматизація браузера",
        "webdriver-manager": "Управління ChromeDriver",
        "requests": "HTTP запити",
        "beautifulsoup4": "Парсинг HTML",
        "colorama": "Кольоровий вивід",
        "tabulate": "Форматування таблиць"
    }
    
    available = []
    missing = []
    
    for dep, description in dependencies.items():
        try:
            __import__(dep.replace("-", "_"))
            print(f"   ✅ {dep:<20} - {description}")
            available.append(dep)
        except ImportError:
            print(f"   ❌ {dep:<20} - {description}")
            missing.append(dep)
    
    print(f"\n   📊 Статус: {len(available)}/{len(dependencies)} залежностей доступно")
    
    if missing:
        print(f"   ⚠️  Відсутні: {', '.join(missing)}")
        print("   💡 Встановіть залежності: pip install -r requirements.txt")
    
    return len(missing) == 0

def check_chrome():
    """Перевірка Chrome браузера"""
    print("\n🌐 Перевірка Chrome браузера...")
    
    chrome_paths = []
    
    if platform.system() == "Windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
    elif platform.system() == "Darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
    else:  # Linux
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"   ✅ Chrome знайдено: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("   ❌ Chrome не знайдено")
        print("   💡 Встановіть Google Chrome для роботи агента")
    
    return chrome_found

def check_file_permissions():
    """Перевірка прав доступу до файлів"""
    print("\n🔐 Перевірка прав доступу...")
    
    files_to_check = [
        "requirements.txt",
        "config.py",
        "ukrzaliznytsia_agent_v2.py"
    ]
    
    all_ok = True
    for file in files_to_check:
        if os.path.exists(file):
            if os.access(file, os.R_OK):
                print(f"   ✅ {file} - доступний для читання")
            else:
                print(f"   ❌ {file} - немає прав на читання")
                all_ok = False
        else:
            print(f"   ❌ {file} - файл не знайдено")
            all_ok = False
    
    return all_ok

def show_recommendations():
    """Показ рекомендацій"""
    print("\n💡 Рекомендації:")
    
    if platform.system() == "Windows":
        print("   1. Запустіть install.bat для автоматичного встановлення")
        print("   2. Або створіть віртуальне середовище вручну:")
        print("      python -m venv venv")
        print("      venv\\Scripts\\activate.bat")
        print("      pip install -r requirements.txt")
    else:
        print("   1. Запустіть ./install.sh для автоматичного встановлення")
        print("   2. Або створіть віртуальне середовище вручну:")
        print("      python3 -m venv venv")
        print("      source venv/bin/activate")
        print("      pip install -r requirements.txt")
    
    print("\n   3. Після встановлення запустіть:")
    print("      python quick_test.py          # Швидкий тест")
    print("      python example_usage.py       # Приклади використання")
    print("      python ukrzaliznytsia_agent_v2.py  # Основний агент")

def main():
    """Головна функція"""
    print("=" * 70)
    print("🔍 ПЕРЕВІРКА СИСТЕМИ ДЛЯ АГЕНТА ПОШУКУ КВИТКІВ")
    print("=" * 70)
    print(f"Час перевірки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Виконання перевірок
    python_ok = check_python_version()
    check_platform()
    pip_ok = check_pip()
    venv_ok = check_virtual_env()
    deps_ok = check_dependencies()
    chrome_ok = check_chrome()
    files_ok = check_file_permissions()
    
    # Підсумок
    print("\n" + "=" * 70)
    print("📊 ПІДСУМОК ПЕРЕВІРКИ")
    print("=" * 70)
    
    checks = [
        ("Python 3.8+", python_ok),
        ("pip", pip_ok),
        ("Віртуальне середовище", venv_ok),
        ("Залежності", deps_ok),
        ("Chrome браузер", chrome_ok),
        ("Файли проекту", files_ok)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_result in checks:
        status = "✅" if check_result else "❌"
        print(f"{status} {check_name}")
        if check_result:
            passed += 1
    
    print(f"\n📈 Результат: {passed}/{total} перевірок пройдено")
    
    if passed == total:
        print("🎉 Система готова до роботи! Можна запускати агента.")
    elif passed >= total * 0.7:
        print("⚠️  Система майже готова. Встановіть відсутні компоненти.")
    else:
        print("❌ Система не готова. Виконайте рекомендації нижче.")
    
    # Рекомендації
    if not (python_ok and pip_ok and deps_ok):
        show_recommendations()
    
    print("=" * 70)
    print("📚 Детальна документація: README.md та PROJECT_INFO.md")
    print("🚀 Швидкий старт: python demo.py")
    print("=" * 70)

if __name__ == "__main__":
    main()