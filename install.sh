#!/bin/bash

# Скрипт встановлення залежностей для агента пошуку квитків Укрзалізниці

echo "🚂 Встановлення залежностей для агента пошуку квитків Укрзалізниці"
echo "=================================================================="

# Перевірка наявності Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не знайдено. Встановіть Python 3.8+ та спробуйте ще раз."
    exit 1
fi

echo "✅ Python знайдено: $(python3 --version)"

# Перевірка наявності pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не знайдено. Встановіть pip та спробуйте ще раз."
    exit 1
fi

echo "✅ pip знайдено: $(pip3 --version)"

# Створення віртуального середовища
echo ""
echo "📱 Створення віртуального середовища..."

if [ -d "venv" ]; then
    echo "⚠️  Віртуальне середовище вже існує. Видаляю..."
    rm -rf venv
fi

python3 -m venv venv

if [ $? -eq 0 ]; then
    echo "✅ Віртуальне середовище створено"
else
    echo "❌ Помилка створення віртуального середовища"
    exit 1
fi

# Активація віртуального середовища
echo ""
echo "🔧 Активація віртуального середовища..."
source venv/bin/activate

if [ $? -eq 0 ]; then
    echo "✅ Віртуальне середовище активовано"
else
    echo "❌ Помилка активації віртуального середовища"
    exit 1
fi

# Оновлення pip
echo ""
echo "⬆️  Оновлення pip..."
pip install --upgrade pip

# Встановлення залежностей
echo ""
echo "📦 Встановлення залежностей з requirements.txt..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo "✅ Всі залежності встановлено успішно"
    else
        echo "❌ Помилка встановлення залежностей"
        exit 1
    fi
else
    echo "❌ Файл requirements.txt не знайдено"
    exit 1
fi

# Перевірка встановлення
echo ""
echo "🔍 Перевірка встановлених пакетів..."
pip list | grep -E "(selenium|webdriver-manager|requests|beautifulsoup4|colorama|tabulate)"

# Тест імпорту
echo ""
echo "🧪 Тест імпорту основних модулів..."

python3 -c "
try:
    import selenium
    print('✅ selenium')
except ImportError:
    print('❌ selenium')

try:
    import webdriver_manager
    print('✅ webdriver-manager')
except ImportError:
    print('❌ webdriver-manager')

try:
    import requests
    print('✅ requests')
except ImportError:
    print('❌ requests')

try:
    import bs4
    print('✅ beautifulsoup4')
except ImportError:
    print('❌ beautifulsoup4')

try:
    import colorama
    print('✅ colorama')
except ImportError:
    print('❌ colorama')

try:
    import tabulate
    print('✅ tabulate')
except ImportError:
    print('❌ tabulate')
"

echo ""
echo "🎉 Встановлення завершено!"
echo ""
echo "📋 Для використання:"
echo "   1. Активуйте віртуальне середовище: source venv/bin/activate"
echo "   2. Запустіть тест: python quick_test.py"
echo "   3. Запустіть приклади: python example_usage.py"
echo "   4. Використовуйте агента: python ukrzaliznytsia_agent_v2.py"
echo ""
echo "🔒 Для деактивації віртуального середовища: deactivate"
echo ""
echo "=================================================================="