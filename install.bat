@echo off
chcp 65001 >nul
echo 🚂 Встановлення залежностей для агента пошуку квитків Укрзалізниці
echo ==================================================================

REM Перевірка наявності Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не знайдено. Встановіть Python 3.8+ та спробуйте ще раз.
    pause
    exit /b 1
)

echo ✅ Python знайдено:
python --version

REM Перевірка наявності pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip не знайдено. Встановіть pip та спробуйте ще раз.
    pause
    exit /b 1
)

echo ✅ pip знайдено:
pip --version

REM Створення віртуального середовища
echo.
echo 📱 Створення віртуального середовища...

if exist "venv" (
    echo ⚠️  Віртуальне середовище вже існує. Видаляю...
    rmdir /s /q venv
)

python -m venv venv

if %errorlevel% equ 0 (
    echo ✅ Віртуальне середовище створено
) else (
    echo ❌ Помилка створення віртуального середовища
    pause
    exit /b 1
)

REM Активація віртуального середовища
echo.
echo 🔧 Активація віртуального середовища...
call venv\Scripts\activate.bat

if %errorlevel% equ 0 (
    echo ✅ Віртуальне середовище активовано
) else (
    echo ❌ Помилка активації віртуального середовища
    pause
    exit /b 1
)

REM Оновлення pip
echo.
echo ⬆️  Оновлення pip...
python -m pip install --upgrade pip

REM Встановлення залежностей
echo.
echo 📦 Встановлення залежностей з requirements.txt...

if exist "requirements.txt" (
    pip install -r requirements.txt
    
    if %errorlevel% equ 0 (
        echo ✅ Всі залежності встановлено успішно
    ) else (
        echo ❌ Помилка встановлення залежностей
        pause
        exit /b 1
    )
) else (
    echo ❌ Файл requirements.txt не знайдено
    pause
    exit /b 1
)

REM Перевірка встановлення
echo.
echo 🔍 Перевірка встановлених пакетів...
pip list | findstr /i "selenium webdriver-manager requests beautifulsoup4 colorama tabulate"

REM Тест імпорту
echo.
echo 🧪 Тест імпорту основних модулів...

python -c "import selenium; print('✅ selenium')" 2>nul || echo ❌ selenium
python -c "import webdriver_manager; print('✅ webdriver-manager')" 2>nul || echo ❌ webdriver-manager
python -c "import requests; print('✅ requests')" 2>nul || echo ❌ requests
python -c "import bs4; print('✅ beautifulsoup4')" 2>nul || echo ❌ beautifulsoup4
python -c "import colorama; print('✅ colorama')" 2>nul || echo ❌ colorama
python -c "import tabulate; print('✅ tabulate')" 2>nul || echo ❌ tabulate

echo.
echo 🎉 Встановлення завершено!
echo.
echo 📋 Для використання:
echo    1. Активуйте віртуальне середовище: venv\Scripts\activate.bat
echo    2. Запустіть тест: python quick_test.py
echo    3. Запустіть приклади: python example_usage.py
echo    4. Використовуйте агента: python ukrzaliznytsia_agent_v2.py
echo.
echo 🔒 Для деактивації віртуального середовища: deactivate
echo.
echo ==================================================================
pause