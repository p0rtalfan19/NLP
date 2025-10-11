#!/usr/bin/env python3
"""
Этап 5: Обучение подсловных моделей токенизации
"""
import json
import os
from subword_models import SubwordModelTrainer

def main():
    print("=" * 60)
    print("ЭТАП 5: ОБУЧЕНИЕ ПОДСЛОВНЫХ МОДЕЛЕЙ ТОКЕНИЗАЦИИ")
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
    print(f"📝 Извлечено {len(texts)} текстов для обучения")
    
    # Создание тренера
    trainer = SubwordModelTrainer(language='russian')
    
    # Размеры словаря для обучения
    vocab_sizes = [8000, 16000, 32000]
    print(f"🎯 Размеры словаря для обучения: {vocab_sizes}")
    
    print("🚀 Начинаем обучение подсловных моделей...")
    print("⏳ Это может занять некоторое время...")
    
    # Обучение всех моделей
    results = trainer.train_all_models(texts, vocab_sizes)
    
    print(f"✅ Обучение завершено")
    print(f"💾 Результаты сохранены в subword_models_results.json")
    print(f"📊 Сравнительная таблица сохранена в subword_models_comparison.csv")
    
    # Вывод результатов
    if 'evaluation_results' in results:
        print(f"\n📈 Результаты оценки подсловных моделей:")
        print(f"{'Модель':<25} {'Фрагментация':<15} {'Сжатие':<10} {'Время (с)':<10} {'Токенов/с':<10}")
        print("-" * 80)
        
        for model_name, metrics in results['evaluation_results'].items():
            print(f"{model_name:<25} {metrics['fragmentation_rate']:<15.4f} {metrics['compression_ratio']:<10.4f} {metrics['avg_processing_time']:<10.4f} {metrics['tokens_per_second']:<10.2f}")
        
        # Рекомендации
        best_fragmentation = min(results['evaluation_results'].items(), key=lambda x: x[1]['fragmentation_rate'])
        fastest_subword = min(results['evaluation_results'].items(), key=lambda x: x[1]['avg_processing_time'])
        best_compression = max(results['evaluation_results'].items(), key=lambda x: x[1]['compression_ratio'])
        
        print(f"\n🏆 Рекомендации:")
        print(f"   Лучшая по фрагментации: {best_fragmentation[0]} ({best_fragmentation[1]['fragmentation_rate']:.4f})")
        print(f"   Самая быстрая: {fastest_subword[0]} ({fastest_subword[1]['avg_processing_time']:.4f}с)")
        print(f"   Лучшая по сжатию: {best_compression[0]} ({best_compression[1]['compression_ratio']:.4f})")
    
    print("\n🎉 Этап 5 завершен!")

if __name__ == "__main__":
    main()

