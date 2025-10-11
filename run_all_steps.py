#!/usr/bin/env python3
"""
Главный скрипт для выполнения всех этапов задания
"""
import os
import sys
import subprocess

def run_step(step_number, script_name):
    """Запуск отдельного этапа"""
    print(f"\n{'='*60}")
    print(f"ЗАПУСК ЭТАПА {step_number}")
    print(f"{'='*60}")
    
    if not os.path.exists(script_name):
        print(f"❌ Скрипт {script_name} не найден!")
        return False
    
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"✅ Этап {step_number} выполнен успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка в этапе {step_number}: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⏹️ Этап {step_number} прерван пользователем")
        return False

def main():
    print("🚀 ЗАПУСК ВСЕХ ЭТАПОВ ЗАДАНИЯ")
    print("=" * 60)
    print("Этапы:")
    print("1. Формирование экспериментального корпуса текстов ✅ (уже выполнен)")
    print("2. Предварительная обработка и очистка текста")
    print("3. Проектирование универсального модуля предобработки")
    print("4. Сравнительный анализ методов токенизации и нормализации")
    print("5. Обучение подсловных моделей токенизации")
    print("6. Веб-интерфейс для интерактивного анализа")
    print("7. Публикация моделей в Hugging Face Hub (опционально)")
    
    # Проверяем наличие исходных данных
    if not os.path.exists("kommersant_articles.jsonl"):
        print(f"\n❌ Файл kommersant_articles.jsonl не найден!")
        print("💡 Сначала запустите парсер: python kommersant_parser.py")
        return
    
    print(f"\n📁 Найден файл с данными: kommersant_articles.jsonl")
    
    # Запуск этапов
    steps = [
        (2, "run_step2.py"),
        (3, "run_step3.py"),
        (4, "run_step4.py"),
        (5, "run_step5.py"),
        (6, "run_step6.py")
    ]
    
    completed_steps = []
    
    for step_number, script_name in steps:
        if run_step(step_number, script_name):
            completed_steps.append(step_number)
        else:
            print(f"\n❌ Этап {step_number} завершился с ошибкой")
            break
    
    # Итоговый отчет
    print(f"\n{'='*60}")
    print(f"ИТОГОВЫЙ ОТЧЕТ")
    print(f"{'='*60}")
    
    if len(completed_steps) == len(steps):
        print("🎉 Все этапы выполнены успешно!")
        print("\n📁 Созданные файлы:")
        files = [
            "kommersant_articles_cleaned.jsonl",
            "kommersant_articles_processed.jsonl", 
            "preprocessing_config.json",
            "tokenization_analysis_results.json",
            "tokenization_metrics.csv",
            "subword_models_results.json",
            "subword_models_comparison.csv"
        ]
        
        for file in files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"   ✅ {file} ({size:,} байт)")
            else:
                print(f"   ❌ {file} (не найден)")
        
        print(f"\n🌐 Для веб-интерфейса запустите:")
        print(f"   python run_step6.py")
        
    else:
        print(f"⚠️ Выполнено этапов: {len(completed_steps)}/{len(steps)}")
        print(f"✅ Завершенные этапы: {completed_steps}")
    
    print(f"\n📊 Требования к корпусу:")
    print(f"   • Общий объём: не менее 50 000 слов")
    print(f"   • Формат хранения: JSONL")
    print(f"   • Структура: заголовок, текст, дата, URL, категория")

if __name__ == "__main__":
    main()

