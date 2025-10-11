#!/usr/bin/env python3
"""
Этап 4: Сравнительный анализ методов токенизации и нормализации
"""
import json
import os
import nltk
from tokenization_analysis import TokenizationAnalyzer

def main():
    nltk.download('punkt_tab')
    print("=" * 60)
    print("ЭТАП 4: АНАЛИЗ МЕТОДОВ ТОКЕНИЗАЦИИ И НОРМАЛИЗАЦИИ")
    print("=" * 60)
    
    # Загрузка обработанных данных
    input_file = "kommersant_articles_processed.jsonl"
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден! Сначала запустите этап 3.")
        return
    
    print(f"📁 Загружаем обработанные данные из {input_file}...")
    articles = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                articles.append(json.loads(line))
    
    print(f"✅ Загружено {len(articles)} статей")
    
    # Извлечение текстов
    texts = [article['text'] for article in articles]
    print(f"📝 Извлечено {len(texts)} текстов для анализа")
    
    # Создание анализатора
    analyzer = TokenizationAnalyzer(language='russian')
    
    print("🔍 Начинаем анализ токенизации...")
    
    # Анализ корпуса
    results = analyzer.analyze_corpus(texts, test_size=0.2)
    
    # Сохранение результатов
    results_file = "tokenization_analysis_results.json"
    analyzer.save_results(results, results_file)
    
    print(f"✅ Анализ завершен")
    print(f"💾 Результаты сохранены в {results_file}")
    print(f"📊 Сравнительная таблица сохранена в tokenization_metrics.csv")
    
    # Вывод результатов
    if 'comparison' in results:
        print(f"\n📈 Результаты сравнения методов токенизации:")
        print(f"{'Метод':<15} {'OOV Rate':<10} {'Семантическое сходство':<20} {'Время (с)':<10}")
        print("-" * 60)
        
        for method, metrics in results['comparison'].items():
            print(f"{method:<15} {metrics['oov_rate']:<10.4f} {metrics['semantic_similarity']:<20.4f} {metrics['train_processing_time']:<10.4f}")
        
        # Рекомендации
        best_oov = min(results['comparison'].items(), key=lambda x: x[1]['oov_rate'])
        fastest = min(results['comparison'].items(), key=lambda x: x[1]['train_processing_time'])
        
        print(f"\n🏆 Рекомендации:")
        print(f"   Лучший по OOV rate: {best_oov[0]} ({best_oov[1]['oov_rate']:.4f})")
        print(f"   Самый быстрый: {fastest[0]} ({fastest[1]['train_processing_time']:.4f}с)")
    
    print("\n🎉 Этап 4 завершен!")

if __name__ == "__main__":
    main()

