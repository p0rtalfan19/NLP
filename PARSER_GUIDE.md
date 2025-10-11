# Руководство по использованию парсеров новостей

## 🚀 Быстрый старт

### 1. Парсер Lenta.ru

```python
from lenta_parser import LentaParser

# Создание парсера
parser = LentaParser(delay=1.0)  # Задержка между запросами

# Парсинг одной категории
articles = parser.parse_category('news', max_articles=50)

# Парсинг всех категорий
all_articles = parser.parse_all_categories(max_articles_per_category=30)

# Сохранение результатов
parser.save_articles(articles, "lenta_articles.jsonl")
```

### 2. Универсальный парсер

```python
from universal_news_parser import UniversalNewsParser

# Создание парсера
parser = UniversalNewsParser(delay=1.0)

# Парсинг конкретного сайта
articles = parser.parse_site('lenta.ru', max_articles_per_category=20)

# Парсинг всех доступных сайтов
all_articles = parser.parse_all_sites(max_articles_per_category=15)

# Сохранение результатов
parser.save_articles(articles, "news_articles.jsonl")
```

## 📋 Доступные категории

### Lenta.ru
- `russia` - Россия
- `world` - Мир
- `economics` - Экономика
- `sport` - Спорт
- `culture` - Культура
- `media` - Медиа
- `science` - Наука
- `style` - Стиль жизни
- `news` - Новости

### TASS.ru
- `politics` - Политика
- `economy` - Экономика
- `society` - Общество
- `world` - Мир
- `sport` - Спорт
- `culture` - Культура
- `science` - Наука
- `technology` - Технологии

### Meduza.io
- `news` - Новости
- `feature` - Репортажи
- `episodes` - Подкасты
- `cards` - Карточки

## 🔧 Настройка

### Параметры парсера

```python
parser = LentaParser(
    delay=1.0,  # Задержка между запросами (секунды)
    base_url="https://lenta.ru"  # Базовый URL
)
```

### Настройка универсального парсера

```python
parser = UniversalNewsParser(delay=1.0)

# Добавление нового сайта
parser.site_configs['new_site.ru'] = {
    'base_url': 'https://new_site.ru',
    'article_patterns': [r'/news/', r'/articles/'],
    'title_selectors': ['h1.title', '.article-title'],
    'text_selectors': ['.article-text', '.content'],
    'date_selectors': ['.date', 'meta[property="article:published_time"]'],
    'category_selectors': ['.category', 'meta[property="article:section"]'],
    'categories': {
        'news': '/news/',
        'politics': '/politics/'
    }
}
```

## 📊 Структура данных

Каждая статья содержит следующие поля:

```json
{
    "title": "Заголовок статьи",
    "text": "Основной текст статьи",
    "date": "2024-01-15T10:30:00",
    "url": "https://lenta.ru/news/2024/01/15/article/",
    "category": "news",
    "tags": ["тег1", "тег2"],
    "author": "Автор статьи",
    "source": "lenta.ru",
    "parsed_at": "2024-01-15T12:00:00"
}
```

## 🧪 Тестирование

Запустите тестовый скрипт для проверки работы парсеров:

```bash
python test_lenta_parser.py
```

## ⚠️ Важные замечания

1. **Соблюдайте задержки**: Используйте задержки между запросами, чтобы не перегружать серверы
2. **Проверяйте robots.txt**: Убедитесь, что парсинг разрешен правилами сайта
3. **Обрабатывайте ошибки**: Всегда используйте try-catch для обработки ошибок сети
4. **Сохраняйте результаты**: Регулярно сохраняйте промежуточные результаты

## 🔍 Отладка

### Включение подробного логирования

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Проверка доступности сайта

```python
import requests

def check_site_availability(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except:
        return False

# Проверка
if check_site_availability("https://lenta.ru"):
    print("Сайт доступен")
else:
    print("Сайт недоступен")
```

## 📈 Производительность

### Рекомендуемые настройки

- **Задержка**: 1-2 секунды между запросами
- **Таймаут**: 10 секунд на запрос
- **Количество статей**: 20-50 на категорию для тестирования
- **Параллельность**: Не рекомендуется для избежания блокировок

### Оптимизация

```python
# Использование сессии для переиспользования соединений
parser = LentaParser()
parser.session.headers.update({
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive'
})
```

## 🚨 Обработка ошибок

```python
try:
    articles = parser.parse_category('news', max_articles=50)
except requests.exceptions.RequestException as e:
    print(f"Ошибка сети: {e}")
except Exception as e:
    print(f"Общая ошибка: {e}")
```

## 📝 Примеры использования

### Сбор корпуса для анализа

```python
from lenta_parser import LentaParser

parser = LentaParser(delay=1.0)

# Сбор статей из разных категорий
categories = ['news', 'russia', 'world', 'economics']
all_articles = []

for category in categories:
    articles = parser.parse_category(category, max_articles=25)
    all_articles.extend(articles)
    print(f"Собрано {len(articles)} статей из категории {category}")

# Сохранение полного корпуса
parser.save_articles(all_articles, "full_corpus.jsonl")
print(f"Всего собрано {len(all_articles)} статей")
```

### Интеграция с основным пайплайном

```python
from nlp import NLPAnalysisPipeline

# Создание пайплайна
pipeline = NLPAnalysisPipeline(language='russian')

# Сбор данных с использованием универсального парсера
articles = pipeline.collect_news_corpus(
    max_articles=200, 
    use_universal=True,  # Использовать универсальный парсер
    save_to_file=True
)

# Продолжение анализа
processed = pipeline.preprocess_corpus()
analysis = pipeline.analyze_tokenization()
```
