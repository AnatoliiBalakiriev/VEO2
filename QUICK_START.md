# 🚀 Швидкий старт

## ⚡ Миттєвий запуск (5 хвилин)

### 1. Перевірка системи
```bash
python3 check_python.py
```

### 2. Автоматичне встановлення

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
install.bat
```

### 3. Запуск агента
```bash
# Активація віртуального середовища
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate.bat  # Windows

# Запуск основного агента
python ukrzaliznytsia_agent_v2.py
```

## 🔧 Ручне встановлення

### Крок 1: Створення віртуального середовища
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate.bat  # Windows
```

### Крок 2: Встановлення залежностей
```bash
pip install -r requirements.txt
```

### Крок 3: Перевірка встановлення
```bash
python quick_test.py
```

## 📱 Перший запуск

### Базовий пошук квитків
```python
from ukrzaliznytsia_agent_v2 import UkrzaliznytsiaAgentV2

with UkrzaliznytsiaAgentV2() as agent:
    # Відкриття сайту
    agent.open_website()
    
    # Пошук квитків
    tickets = agent.search_tickets("Київ", "Львів", "25.12.2024")
    
    # Відображення результатів
    agent.display_tickets(tickets)
    
    # Збереження у файл
    agent.save_tickets(tickets, format_type="json")
```

## 🎯 Швидкі команди

### Демонстрація (без встановлення)
```bash
python3 demo.py
```

### Тестування
```bash
python3 quick_test.py
```

### Приклади використання
```bash
python3 example_usage.py
```

### Перевірка системи
```bash
python3 check_python.py
```

## 🚨 Вирішення проблем

### Помилка "Chrome не знайдено"
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install google-chrome-stable

# CentOS/RHEL
sudo yum install google-chrome-stable

# macOS
brew install --cask google-chrome

# Windows
# Завантажте з https://www.google.com/chrome/
```

### Помилка "selenium не знайдено"
```bash
pip install selenium
```

### Помилка "webdriver-manager не знайдено"
```bash
pip install webdriver-manager
```

## 📚 Наступні кроки

1. **Вивчіть приклади** в `example_usage.py`
2. **Налаштуйте конфігурацію** в `config.py`
3. **Перегляньте документацію** в `README.md`
4. **Дослідіть функції** агента

## 💡 Поради

- Запускайте агента в **headless режимі** для серверів
- Використовуйте **віртуальне середовище** для ізоляції залежностей
- **Логуйте** всі дії для діагностики
- **Поважайте** обмеження сайту Укрзалізниці

---

**Готово! Ваш агент пошуку квитків готовий до роботи! 🚂✨**