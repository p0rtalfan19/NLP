#!/usr/bin/env python3
"""
Этап 2: Предварительная обработка и очистка текста
"""
import json
import os
from text_cleaner import TextCleaner

def main():
    print("=" * 60)
    print("ЭТАП 2: ПРЕДВАРИТЕЛЬНАЯ ОБРАБОТКА И ОЧИСТКА ТЕКСТА")
    print("=" * 60)
    
    # Загрузка данных
    input_file = "kommersant_articles.jsonl"
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден!")
        return
    
    print(f"📁 Загружаем данные из {input_file}...")
    articles = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                articles.append(json.loads(line))
    
    print(f"✅ Загружено {len(articles)} статей")
    
    # Создание очистителя текста
    cleaner = TextCleaner(remove_stopwords=True, language='russian')
    
    print("🧹 Начинаем очистку текстов...")
    
    # Очистка статей
    cleaned_articles = cleaner.batch_clean(
        articles,
        clean_title=True,
        clean_text=True,
        remove_html=True,
        remove_urls=True,
        remove_phones=True,
        remove_dates=True,
        remove_numbers=False,  # Оставляем числа для анализа
        normalize_whitespace=True,
        normalize_punctuation=True,
        to_lowercase=False,  # Сохраняем регистр
        remove_stopwords=True
    )
    
    # Сохранение очищенных данных
    output_file = "kommersant_articles_cleaned.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for article in cleaned_articles:
            f.write(json.dumps(article, ensure_ascii=False) + '\n')
    
    print(f"✅ Очищено {len(cleaned_articles)} статей")
    print(f"💾 Результат сохранен в {output_file}")
    
    # Статистика
    total_words_before = sum(len(article['text'].split()) for article in articles)
    total_words_after = sum(len(article['text'].split()) for article in cleaned_articles)
    
    print(f"\n📊 Статистика:")
    print(f"   Слов до очистки: {total_words_before:,}")
    print(f"   Слов после очистки: {total_words_after:,}")
    print(f"   Сокращение: {((total_words_before - total_words_after) / total_words_before * 100):.1f}%")
    
    print("\n🎉 Этап 2 завершен!")

if __name__ == "__main__":
    main()
