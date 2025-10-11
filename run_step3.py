#!/usr/bin/env python3
"""
Этап 3: Проектирование универсального модуля предобработки
"""
import json
import os
from universal_preprocessor import UniversalPreprocessor, PreprocessingConfig

def main():
    print("=" * 60)
    print("ЭТАП 3: УНИВЕРСАЛЬНЫЙ МОДУЛЬ ПРЕДОБРАБОТКИ")
    print("=" * 60)
    
    # Загрузка очищенных данных
    input_file = "kommersant_articles_cleaned.jsonl"
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден! Сначала запустите этап 2.")
        return
    
    print(f"📁 Загружаем очищенные данные из {input_file}...")
    articles = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                articles.append(json.loads(line))
    
    print(f"✅ Загружено {len(articles)} статей")
    
    # Создание конфигурации предобработки
    config = PreprocessingConfig(
        replace_numbers=True,        # Заменить числа на <NUM>
        replace_urls=True,          # Заменить URL на <URL>
        replace_emails=True,        # Заменить email на <EMAIL>
        replace_phones=True,        # Заменить телефоны на <PHONE>
        replace_dates=True,         # Заменить даты на <DATE>
        replace_times=True,          # Заменить время на <TIME>
        replace_currencies=True,    # Заменить валюты на <CURRENCY>
        normalize_punctuation=True, # Нормализовать пунктуацию
        normalize_quotes=True,       # Нормализовать кавычки
        normalize_dashes=True,       # Нормализовать тире
        normalize_spaces=True,       # Нормализовать пробелы
        expand_abbreviations=True,   # Расшифровать сокращения
        to_lowercase=False          # Сохранить регистр
    )
    
    # Создание предпроцессора
    preprocessor = UniversalPreprocessor(config, language='russian')
    
    print("🔄 Начинаем предобработку текстов...")
    
    # Предобработка статей
    processed_articles = preprocessor.batch_preprocess(articles)
    
    # Сохранение обработанных данных
    output_file = "kommersant_articles_processed.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for article in processed_articles:
            f.write(json.dumps(article, ensure_ascii=False) + '\n')
    
    print(f"✅ Обработано {len(processed_articles)} статей")
    print(f"💾 Результат сохранен в {output_file}")
    
    # Сохранение конфигурации
    config_file = "preprocessing_config.json"
    preprocessor.save_config(config_file)
    print(f"⚙️ Конфигурация сохранена в {config_file}")
    
    # Статистика
    total_words_before = sum(len(article['text'].split()) for article in articles)
    total_words_after = sum(len(article['text'].split()) for article in processed_articles)
    
    print(f"\n📊 Статистика:")
    print(f"   Слов до предобработки: {total_words_before:,}")
    print(f"   Слов после предобработки: {total_words_after:,}")
    print(f"   Изменение: {((total_words_after - total_words_before) / total_words_before * 100):+.1f}%")
    
    # Пример обработки
    if processed_articles:
        print(f"\n📝 Пример обработки:")
        print(f"   Исходный текст: {articles[0]['text'][:100]}...")
        print(f"   Обработанный: {processed_articles[0]['text'][:100]}...")
    
    print("\n🎉 Этап 3 завершен!")

if __name__ == "__main__":
    main()

