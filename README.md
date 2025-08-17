# Агент пошуку квитків Укрзалізниці 🚂

Автоматизований агент для пошуку та аналізу квитків на поїзди на сайті Укрзалізниці.

## 🌟 Особливості

- **Автоматизований пошук** квитків за маршрутом та датою
- **Підтримка множинних маршрутів** та діапазонів дат
- **Розширена фільтрація** за ціною, часом, типом поїзда
- **Збереження результатів** у різних форматах (JSON, CSV, TXT)
- **Налаштовувана конфігурація** та логування
- **Обмеження частоти запитів** для безпечного використання
- **Підтримка проксі** та ротація IP-адрес
- **Кольоровий вивід** та зручні таблиці результатів

## 📋 Вимоги

- Python 3.8+
- Google Chrome браузер
- Інтернет-з'єднання

## 🚀 Встановлення

1. **Клонуйте репозиторій:**
```bash
git clone <repository-url>
cd ukrzaliznytsia-agent
```

2. **Створіть віртуальне середовище:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate  # Windows
```

3. **Встановіть залежності:**
```bash
pip install -r requirements.txt
```

4. **Перевірте конфігурацію:**
```bash
python config.py
```

## 💻 Використання

### Базовий пошук

```python
from ukrzaliznytsia_agent_v2 import UkrzaliznytsiaAgentV2
from datetime import datetime, timedelta

# Створення агента
with UkrzaliznytsiaAgentV2(headless=False) as agent:
    # Відкриття сайту
    agent.open_website()
    
    # Пошук квитків
    from_station = "Київ"
    to_station = "Львів"
    date = (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")
    
    tickets = agent.search_tickets(from_station, to_station, date)
    
    if tickets:
        # Відображення результатів
        agent.display_tickets(tickets, "table")
        
        # Збереження у файл
        agent.save_tickets(tickets, format_type="json")
```

### Пошук для кількох маршрутів

```python
# Популярні маршрути
routes = [
    ("Київ", "Харків"),
    ("Київ", "Одеса"),
    ("Львів", "Київ")
]

# Пошук для всіх маршрутів
results = agent.search_multiple_routes(routes, date)

for route, tickets in results.items():
    print(f"Маршрут {route}: {len(tickets)} квитків")
```

### Пошук для діапазону дат

```python
from datetime import datetime, timedelta

start_date = datetime.now() + timedelta(days=1)
end_date = datetime.now() + timedelta(days=30)

tickets = agent.search_date_range(from_station, to_station, start_date, end_date)
print(f"Знайдено {len(tickets)} квитків для діапазону дат")
```

### Фільтрація результатів

```python
# Фільтрація за ціною
affordable_tickets = agent.filter_tickets(tickets, max_price=1000)

# Фільтрація за часом відправлення (ранкові поїзди)
morning_tickets = agent.filter_tickets(tickets, departure_time_range=(6, 12))

# Фільтрація за типом поїзда
express_tickets = agent.filter_tickets(tickets, train_types=["Швидкий", "Експрес"])
```

### Збереження результатів

```python
# Збереження у різних форматах
agent.save_tickets(tickets, format_type="json")    # JSON
agent.save_tickets(tickets, format_type="csv")     # CSV
agent.save_tickets(tickets, format_type="txt")     # Текстовий файл

# Збереження з власною назвою файлу
agent.save_tickets(tickets, filename="my_tickets.json")
```

## ⚙️ Конфігурація

### Основні налаштування

Відредагуйте файл `config.py` для налаштування:

```python
# Браузер
BROWSER_CONFIG = {
    "headless": False,        # Запуск у фоновому режимі
    "timeout": 10,            # Таймаут очікування (секунди)
    "window_size": "1920,1080"
}

# Пошук
SEARCH_CONFIG = {
    "delay_between_searches": 2,  # Затримка між пошуками
    "max_retries": 3              # Максимальна кількість спроб
}

# Безпека
SECURITY_CONFIG = {
    "rate_limiting": True,        # Обмеження частоти запитів
    "max_requests_per_minute": 30 # Максимум запитів на хвилину
}
```

### Змінні середовища

```bash
# Запуск у фоновому режимі
export HEADLESS=true

# Налаштування таймаутів
export BROWSER_TIMEOUT=15
export SEARCH_DELAY=3

# Максимальна кількість спроб
export MAX_RETRIES=5
```

## 📁 Структура проекту

```
ukrzaliznytsia-agent/
├── ukrzaliznytsia_agent.py          # Базова версія агента
├── ukrzaliznytsia_agent_v2.py       # Покращена версія з конфігурацією
├── config.py                         # Файл конфігурації
├── example_usage.py                  # Приклади використання
├── requirements.txt                  # Залежності Python
├── README.md                         # Документація
└── ukrzaliznytsia.log               # Лог-файл (створюється автоматично)
```

## 🔧 Приклади використання

### Запуск прикладів

```bash
# Базовий пошук
python example_usage.py

# Покращений агент
python ukrzaliznytsia_agent_v2.py
```

### Інтерактивний режим

```bash
python example_usage.py
# Виберіть опцію 5 для інтерактивного пошуку
```

## 📊 Формати виводу

### Таблиця
```
┌─────┬──────────────┬─────────────────────┬─────────────────┬──────────────┬──────────┬─────────┬────────────┐
│  №  │ Номер поїзда │      Маршрут        │      Час        │ Тривалість   │   Ціна   │  Місця  │    Тип     │
├─────┼──────────────┼─────────────────────┼─────────────────┼──────────────┼──────────┼─────────┼────────────┤
│  1  │     001      │   Київ → Львів      │  08:00 - 14:30 │    6:30     │  450 грн │   45    │  Швидкий   │
│  2  │     003      │   Київ → Львів      │  20:00 - 02:30 │    6:30     │  380 грн │   23    │ Нічний     │
└─────┴──────────────┴─────────────────────┴─────────────────┴──────────────┴──────────┴─────────┴────────────┘
```

### Зведення
```
Зведення пошуку:
Всього знайдено: 2 квитки

За типами поїздів:
  Швидкий: 1
  Нічний: 1

За цінами:
  Мінімальна: 380.00 грн
  Максимальна: 450.00 грн
  Середня: 415.00 грн
```

## 🚨 Важливі зауваження

1. **Повага до сайту:** Агент має вбудовані затримки та обмеження частоти запитів
2. **CSS селектори:** Можуть змінюватися при оновленні сайту - перевіряйте `config.py`
3. **Стабільність:** Використовуйте повторні спроби для надійності
4. **Логування:** Всі дії записуються у файл `ukrzaliznytsia.log`

## 🔍 Діагностика проблем

### Поширені помилки

1. **"ChromeDriver не знайдено"**
   ```bash
   pip install --upgrade webdriver-manager
   ```

2. **"Сайт не завантажується"**
   - Перевірте інтернет-з'єднання
   - Спробуйте запустити без headless режиму
   - Перевірте, чи не змінився URL сайту

3. **"Елементи не знайдено"**
   - Оновіть CSS селектори в `config.py`
   - Збільшіть таймаути
   - Перевірте, чи не змінилася структура сайту

### Налагодження

```python
# Увімкнення детального логування
import logging
logging.basicConfig(level=logging.DEBUG)

# Запуск без headless режиму для візуального контролю
agent = UkrzaliznytsiaAgentV2(headless=False)
```

## 🤝 Внесок у проект

1. Форкніть репозиторій
2. Створіть гілку для нової функції
3. Зробіть коміт змін
4. Відправте Pull Request

## 📄 Ліцензія

Цей проект розповсюджується під ліцензією MIT. Дивіться файл `LICENSE` для деталей.

## ⚠️ Відмова від відповідальності

Цей агент призначений тільки для особистого використання та навчальних цілей. Використовуйте його відповідально та з повагою до сайту Укрзалізниці. Автори не несуть відповідальності за будь-які наслідки використання цього коду.

## 📞 Підтримка

Якщо у вас виникли питання або проблеми:

1. Перевірте лог-файл `ukrzaliznytsia.log`
2. Перегляньте приклади в `example_usage.py`
3. Створіть Issue у репозиторії

---

**Удачі у пошуку квитків! 🚂✨**