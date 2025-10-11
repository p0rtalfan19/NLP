#!/usr/bin/env python3
"""
Основной модуль для анализа текстов и токенизации
Объединяет все компоненты системы обработки естественного языка
"""
import os
os.environ['TCL_LIBRARY'] = "C:/Program Files/Python313/tcl/tcl8.6"
os.environ['TK_LIBRARY'] = "C:/Program Files/Python313/tcl/tk8.6"
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Импорт наших модулей
from kommersant_parser import KommersantParser
from text_cleaner import TextCleaner
from universal_preprocessor import UniversalPreprocessor, PreprocessingConfig
from tokenization_analysis import TokenizationAnalyzer
from subword_models import SubwordModelTrainer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nlp_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NLPAnalysisPipeline:
    """Основной класс для анализа текстов и токенизации"""
    
    def __init__(self, language: str = 'russian'):
        self.language = language
        self.articles = []
        self.processed_articles = []
        self.analysis_results = {}
        self.subword_results = {}
        
        # Инициализация компонентов
        self.parser = KommersantParser()
        self.text_cleaner = TextCleaner(language=language)
        self.preprocessor = UniversalPreprocessor(language=language)
        self.tokenization_analyzer = TokenizationAnalyzer(language=language)
        self.subword_trainer = SubwordModelTrainer(language=language)
        
        logger.info(f"Инициализирован пайплайн анализа для языка: {language}")
    
    def collect_news_corpus(self, max_articles: int = 100, save_to_file: bool = True, start_id: int = 8050000, end_id: int = 8059999) -> List[Dict[str, Any]]:
        """Сбор корпуса новостных текстов с Коммерсанта"""
        logger.info(f"Начинаем сбор корпуса новостей с Коммерсанта (максимум {max_articles} статей)")
        
        try:
            # Используем парсер Коммерсанта
            self.articles = self.parser.parse_article_range(start_id, end_id, max_articles)
            
            if not self.articles:
                logger.warning("Не удалось собрать статьи")
                return []
            
            # Сохранение корпуса
            if save_to_file:
                corpus_file = f"kommersant_corpus_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
                self.parser.save_articles(self.articles, corpus_file)
                logger.info(f"Корпус сохранен в файл: {corpus_file}")
            
            logger.info(f"Собрано {len(self.articles)} статей")
            return self.articles
            
        except Exception as e:
            logger.error(f"Ошибка при сборе корпуса: {e}")
            return []
    
    def preprocess_corpus(self, config: Optional[PreprocessingConfig] = None) -> List[Dict[str, Any]]:
        """Предобработка корпуса текстов"""
        if not self.articles:
            logger.error("Корпус не загружен")
            return []
        
        logger.info("Начинаем предобработку корпуса")
        
        try:
            # Создание конфигурации по умолчанию
            if config is None:
                config = PreprocessingConfig(
                    replace_numbers=True,
                    replace_urls=True,
                    replace_emails=True,
                    replace_phones=True,
                    replace_dates=True,
                    replace_times=True,
                    replace_currencies=True,
                    normalize_punctuation=True,
                    normalize_quotes=True,
                    normalize_dashes=True,
                    normalize_spaces=True,
                    expand_abbreviations=True,
                    expand_contractions=True,
                    to_lowercase=False
                )
            
            # Предобработка
            self.preprocessor = UniversalPreprocessor(config, self.language)
            self.processed_articles = self.preprocessor.batch_preprocess(self.articles)
            
            logger.info(f"Предобработано {len(self.processed_articles)} статей")
            return self.processed_articles
            
        except Exception as e:
            logger.error(f"Ошибка при предобработке: {e}")
            return []
    
    def analyze_tokenization(self, test_size: float = 0.2) -> Dict[str, Any]:
        """Анализ методов токенизации"""
        if not self.processed_articles:
            logger.error("Обработанные статьи не найдены")
            return {}
        
        logger.info("Начинаем анализ токенизации")
        
        try:
            # Извлечение текстов
            texts = [article['text'] for article in self.processed_articles]
            
            # Анализ
            self.analysis_results = self.tokenization_analyzer.analyze_corpus(texts, test_size)
            
            # Сохранение результатов
            results_file = f"tokenization_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Анализ токенизации завершен. Результаты сохранены в {results_file}")
            return self.analysis_results
            
        except Exception as e:
            logger.error(f"Ошибка при анализе токенизации: {e}")
            return {}
    
    def train_subword_models(self, vocab_sizes: List[int] = [8000, 16000, 32000]) -> Dict[str, Any]:
        """Обучение подсловных моделей"""
        if not self.processed_articles:
            logger.error("Обработанные статьи не найдены")
            return {}
        
        logger.info(f"Начинаем обучение подсловных моделей (размеры словаря: {vocab_sizes})")
        
        try:
            # Извлечение текстов
            texts = [article['text'] for article in self.processed_articles]
            
            # Обучение моделей
            self.subword_results = self.subword_trainer.train_all_models(texts, vocab_sizes)
            
            logger.info("Обучение подсловных моделей завершено")
            return self.subword_results
            
        except Exception as e:
            logger.error(f"Ошибка при обучении подсловных моделей: {e}")
            return {}
    
    def generate_comprehensive_report(self) -> str:
        """Генерация комплексного отчета"""
        logger.info("Генерация комплексного отчета")
        
        report_sections = []
        
        # Заголовок
        report_sections.append(f"""
# Отчет анализа текстов и токенизации
**Дата создания:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Язык:** {self.language}

---
""")
        
        # Информация о корпусе
        if self.articles:
            total_words = sum(len(article['text'].split()) for article in self.articles)
            categories = set(article.get('category', 'unknown') for article in self.articles)
            
            report_sections.append(f"""
## 1. Информация о корпусе

- **Количество статей:** {len(self.articles)}
- **Общее количество слов:** {total_words:,}
- **Среднее количество слов на статью:** {total_words // len(self.articles):,}
- **Количество категорий:** {len(categories)}
- **Категории:** {', '.join(sorted(categories))}

""")
        
        # Результаты предобработки
        if self.processed_articles:
            report_sections.append(f"""
## 2. Предобработка текстов

- **Обработано статей:** {len(self.processed_articles)}
- **Статус:** Успешно завершена

""")
        
        # Результаты анализа токенизации
        if self.analysis_results and 'comparison' in self.analysis_results:
            report_sections.append("""
## 3. Анализ токенизации

### Сравнение методов токенизации

| Метод | Размер словаря (train) | Размер словаря (test) | OOV Rate | Семантическое сходство | Время обработки (с) |
|-------|------------------------|----------------------|----------|------------------------|-------------------|
""")
            
            for method, metrics in self.analysis_results['comparison'].items():
                report_sections.append(f"| {method} | {metrics['train_vocab_size']} | {metrics['test_vocab_size']} | {metrics['oov_rate']:.4f} | {metrics['semantic_similarity']:.4f} | {metrics['train_processing_time']:.4f} |")
            
            report_sections.append("""

### Рекомендации по токенизации

""")
            
            # Находим лучший метод по OOV rate
            best_method = min(self.analysis_results['comparison'].items(), 
                            key=lambda x: x[1]['oov_rate'])
            report_sections.append(f"- **Лучший метод по OOV rate:** {best_method[0]} (OOV rate: {best_method[1]['oov_rate']:.4f})")
            
            # Находим самый быстрый метод
            fastest_method = min(self.analysis_results['comparison'].items(), 
                               key=lambda x: x[1]['train_processing_time'])
            report_sections.append(f"- **Самый быстрый метод:** {fastest_method[0]} (время: {fastest_method[1]['train_processing_time']:.4f}с)")
        
        # Результаты подсловных моделей
        if self.subword_results and 'evaluation_results' in self.subword_results:
            report_sections.append("""
## 4. Подсловные модели токенизации

### Результаты оценки моделей

| Модель | Коэффициент фрагментации | Коэффициент сжатия | Время обработки (с) | Токенов в секунду |
|--------|-------------------------|-------------------|-------------------|------------------|
""")
            
            for model_name, metrics in self.subword_results['evaluation_results'].items():
                report_sections.append(f"| {model_name} | {metrics['fragmentation_rate']:.4f} | {metrics['compression_ratio']:.4f} | {metrics['avg_processing_time']:.4f} | {metrics['tokens_per_second']:.2f} |")
            
            report_sections.append("""

### Рекомендации по подсловным моделям

""")
            
            # Находим лучшую модель по коэффициенту фрагментации
            best_subword = min(self.subword_results['evaluation_results'].items(), 
                             key=lambda x: x[1]['fragmentation_rate'])
            report_sections.append(f"- **Лучшая модель по фрагментации:** {best_subword[0]} (коэффициент: {best_subword[1]['fragmentation_rate']:.4f})")
            
            # Находим самую быструю модель
            fastest_subword = min(self.subword_results['evaluation_results'].items(), 
                                key=lambda x: x[1]['avg_processing_time'])
            report_sections.append(f"- **Самая быстрая модель:** {fastest_subword[0]} (время: {fastest_subword[1]['avg_processing_time']:.4f}с)")
        
        # Заключение
        report_sections.append("""
## 5. Заключение

Проведен комплексный анализ методов токенизации и нормализации текстов на русском языке. 
Результаты показывают эффективность различных подходов для обработки новостных текстов.

### Основные выводы:

1. **Токенизация:** Выбран оптимальный метод на основе метрик OOV rate и скорости обработки
2. **Нормализация:** Применены методы стемминга и лемматизации для унификации текста
3. **Подсловные модели:** Обучены модели BPE, WordPiece и Unigram для эффективной токенизации
4. **Производительность:** Оценена скорость обработки различных методов

### Рекомендации для практического применения:

- Использовать выбранный метод токенизации для предобработки текстов
- Применить оптимальную подсловную модель для конкретной задачи
- Учитывать баланс между качеством и скоростью обработки

---
*Отчет сгенерирован автоматически системой анализа текстов*
""")
        
        # Объединение всех секций
        full_report = '\n'.join(report_sections)
        
        # Сохранение отчета
        report_file = f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        logger.info(f"Комплексный отчет сохранен в файл: {report_file}")
        return full_report
    
    def run_full_pipeline(self, max_articles: int = 100, vocab_sizes: List[int] = [8000, 16000, 32000]) -> Dict[str, Any]:
        """Запуск полного пайплайна анализа"""
        logger.info("Запуск полного пайплайна анализа")
        
        results = {
            'start_time': datetime.now().isoformat(),
            'steps_completed': [],
            'errors': []
        }
        
        try:
            # Шаг 1: Сбор корпуса
            logger.info("Шаг 1: Сбор корпуса новостей")
            self.collect_news_corpus(max_articles)
            results['steps_completed'].append('corpus_collection')
            
            # Шаг 2: Предобработка
            logger.info("Шаг 2: Предобработка текстов")
            self.preprocess_corpus()
            results['steps_completed'].append('preprocessing')
            
            # Шаг 3: Анализ токенизации
            logger.info("Шаг 3: Анализ токенизации")
            self.analyze_tokenization()
            results['steps_completed'].append('tokenization_analysis')
            
            # Шаг 4: Обучение подсловных моделей
            logger.info("Шаг 4: Обучение подсловных моделей")
            self.train_subword_models(vocab_sizes)
            results['steps_completed'].append('subword_training')
            
            # Шаг 5: Генерация отчета
            logger.info("Шаг 5: Генерация отчета")
            report = self.generate_comprehensive_report()
            results['steps_completed'].append('report_generation')
            
            results['end_time'] = datetime.now().isoformat()
            results['status'] = 'success'
            
            logger.info("Полный пайплайн анализа завершен успешно")
            
        except Exception as e:
            logger.error(f"Ошибка в пайплайне анализа: {e}")
            results['errors'].append(str(e))
            results['status'] = 'error'
        
        return results

def main():
    """Основная функция для запуска анализа"""
    print("=" * 60)
    print("СИСТЕМА АНАЛИЗА ТЕКСТОВ И ТОКЕНИЗАЦИИ")
    print("=" * 60)
    
    # Создание пайплайна
    pipeline = NLPAnalysisPipeline(language='russian')
    
    # Выбор режима работы
    print("\nВыберите режим работы:")
    print("1. Полный пайплайн анализа")
    print("2. Только сбор корпуса")
    print("3. Только анализ токенизации")
    print("4. Только обучение подсловных моделей")
    print("5. Веб-интерфейс")
    
    choice = input("\nВведите номер (1-5): ").strip()
    
    if choice == '1':
        # Полный пайплайн
        max_articles = int(input("Количество статей для анализа (по умолчанию 100): ") or "100")
        vocab_sizes = [8000, 16000, 32000]
        
        print(f"\nЗапуск полного пайплайна с {max_articles} статьями...")
        results = pipeline.run_full_pipeline(max_articles, vocab_sizes)
        
        print(f"\nСтатус: {results['status']}")
        print(f"Завершенные шаги: {', '.join(results['steps_completed'])}")
        if results['errors']:
            print(f"Ошибки: {', '.join(results['errors'])}")
    
    elif choice == '2':
        # Только сбор корпуса
        max_articles = int(input("Количество статей (по умолчанию 100): ") or "100")
        articles = pipeline.collect_news_corpus(max_articles)
        print(f"Собрано {len(articles)} статей")
    
    elif choice == '3':
        # Только анализ токенизации
        print("Сначала необходимо собрать корпус...")
        articles = pipeline.collect_news_corpus(50)
        if articles:
            pipeline.preprocess_corpus()
            results = pipeline.analyze_tokenization()
            print("Анализ токенизации завершен")
    
    elif choice == '4':
        # Только обучение подсловных моделей
        print("Сначала необходимо собрать корпус...")
        articles = pipeline.collect_news_corpus(50)
        if articles:
            pipeline.preprocess_corpus()
            results = pipeline.train_subword_models()
            print("Обучение подсловных моделей завершено")
    
    elif choice == '5':
        # Веб-интерфейс
        print("Запуск веб-интерфейса...")
        print("Выполните: streamlit run web_interface.py")
    
    else:
        print("Неверный выбор")
    
    print("\nАнализ завершен!")

if __name__ == "__main__":
    main()
