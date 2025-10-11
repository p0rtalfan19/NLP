import os
os.environ['TCL_LIBRARY'] = "C:/Program Files/Python313/tcl/tcl8.6"
os.environ['TK_LIBRARY'] = "C:/Program Files/Python313/tcl/tk8.6"
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io
from datetime import datetime
import logging

# Импорт наших модулей
from kommersant_parser import KommersantParser
from text_cleaner import TextCleaner
from universal_preprocessor import UniversalPreprocessor, PreprocessingConfig
from tokenization_analysis import TokenizationAnalyzer
from subword_models import SubwordModelTrainer

# Настройка страницы
st.set_page_config(
    page_title="Анализ текстов и токенизация",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TextAnalysisWebApp:
    """Веб-приложение для анализа текстов и токенизации"""
    
    def __init__(self):
        self.articles = []
        self.processed_articles = []
        self.analysis_results = {}
        
        # Инициализация компонентов
        self.kommersant_parser = KommersantParser()
        self.text_cleaner = TextCleaner()
        self.preprocessor = UniversalPreprocessor()
        self.tokenization_analyzer = TokenizationAnalyzer()
        self.subword_trainer = SubwordModelTrainer()
    
    def load_sample_data(self):
        """Загрузка примеров данных"""
        sample_texts = [
            "Россия и Китай подписали соглашение о сотрудничестве в области технологий.",
            "В Москве состоялась конференция по искусственному интеллекту.",
            "Ученые разработали новый алгоритм машинного обучения.",
            "Компания представила инновационное решение для обработки данных.",
            "Исследователи изучают возможности применения нейронных сетей."
        ]
        
        self.articles = [
            {
                'title': f"Новость {i+1}",
                'text': text,
                'date': datetime.now().isoformat(),
                'url': f"https://example.com/news/{i+1}",
                'category': 'technology',
                'source': 'sample'
            }
            for i, text in enumerate(sample_texts)
        ]
        
        return self.articles
    
    def parse_kommersant_news(self, start_id: int, end_id: int, max_articles: int = 100):
        """Парсинг новостей с Коммерсанта"""
        with st.spinner("Парсинг новостей с Коммерсанта..."):
            try:
                self.articles = self.kommersant_parser.parse_article_range(start_id, end_id, max_articles)
                return self.articles
            except Exception as e:
                st.error(f"Ошибка при парсинге: {e}")
                return []
    
    def preprocess_articles(self, config: PreprocessingConfig):
        """Предобработка статей"""
        if not self.articles:
            return []
        
        self.preprocessor = UniversalPreprocessor(config)
        self.processed_articles = self.preprocessor.batch_preprocess(self.articles)
        return self.processed_articles
    
    def analyze_tokenization(self, texts: list):
        """Анализ токенизации"""
        if not texts:
            return {}
        
        return self.tokenization_analyzer.analyze_corpus(texts)
    
    def train_subword_models(self, texts: list, vocab_sizes: list):
        """Обучение подсловных моделей"""
        if not texts:
            return {}
        
        return self.subword_trainer.train_all_models(texts, vocab_sizes)

def main():
    st.title("📝 Анализ текстов и токенизация")
    st.markdown("---")
    
    # Инициализация приложения
    if 'app' not in st.session_state:
        st.session_state.app = TextAnalysisWebApp()
    
    app = st.session_state.app
    
    # Боковая панель
    with st.sidebar:
        st.header("⚙️ Настройки")
        
        # Загрузка данных
        st.subheader("📁 Загрузка данных")
        data_source = st.selectbox(
            "Источник данных",
            ["Пример данных", "Коммерсантъ", "Загрузить файл"]
        )
        
        if data_source == "Пример данных":
            if st.button("🔄 Загрузить примеры"):
                app.articles = app.load_sample_data()
                st.success(f"Загружено {len(app.articles)} примеров")
        
        elif data_source == "Коммерсантъ":
            col1, col2 = st.columns(2)
            with col1:
                start_id = st.number_input("Начальный ID", value=8050000, min_value=1)
            with col2:
                end_id = st.number_input("Конечный ID", value=8059999, min_value=1)
            max_articles = st.slider("Максимум статей", 10, 500, 100)
            if st.button("🔄 Парсить Коммерсантъ"):
                app.articles = app.parse_kommersant_news(start_id, end_id, max_articles)
                if app.articles:
                    st.success(f"Спарсено {len(app.articles)} статей")
        
        elif data_source == "Загрузить файл":
            uploaded_file = st.file_uploader("Загрузите JSONL файл", type=['jsonl', 'json'])
            if uploaded_file:
                try:
                    content = uploaded_file.read().decode('utf-8')
                    articles = []
                    for line in content.strip().split('\n'):
                        if line:
                            articles.append(json.loads(line))
                    app.articles = articles
                    st.success(f"Загружено {len(articles)} статей")
                except Exception as e:
                    st.error(f"Ошибка при загрузке файла: {e}")
        
        # Настройки предобработки
        st.subheader("🔧 Предобработка")
        
        with st.expander("Настройки предобработки"):
            replace_numbers = st.checkbox("Заменять числа", value=True)
            replace_urls = st.checkbox("Заменять URL", value=True)
            replace_emails = st.checkbox("Заменять email", value=True)
            replace_phones = st.checkbox("Заменять телефоны", value=True)
            replace_dates = st.checkbox("Заменять даты", value=True)
            replace_times = st.checkbox("Заменять время", value=True)
            replace_currencies = st.checkbox("Заменять валюты", value=True)
            normalize_punctuation = st.checkbox("Нормализовать пунктуацию", value=True)
            normalize_quotes = st.checkbox("Нормализовать кавычки", value=True)
            normalize_dashes = st.checkbox("Нормализовать тире", value=True)
            normalize_spaces = st.checkbox("Нормализовать пробелы", value=True)
            expand_abbreviations = st.checkbox("Расшифровывать сокращения", value=True)
            to_lowercase = st.checkbox("Приводить к нижнему регистру", value=False)
        
        # Настройки анализа
        st.subheader("📊 Анализ")
        
        tokenization_methods = st.multiselect(
            "Методы токенизации",
            ["naive", "regex", "nltk", "spacy", "razdel"],
            default=["naive", "nltk", "razdel"]
        )
        
        normalization_methods = st.multiselect(
            "Методы нормализации",
            ["porter_stem", "snowball_stem", "spacy_lemma", "pymorphy_lemma"],
            default=["porter_stem", "snowball_stem"]
        )
        
        vocab_sizes = st.multiselect(
            "Размеры словаря для подсловных моделей",
            [4000, 8000, 16000, 32000],
            default=[8000, 16000]
        )
    
    # Основной контент
    if not app.articles:
        st.info("👈 Загрузите данные в боковой панели для начала анализа")
    else:
        # Информация о данных
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Статей", len(app.articles))
        with col2:
            total_words = sum(len(article['text'].split()) for article in app.articles)
            st.metric("Слов", f"{total_words:,}")
        with col3:
            avg_words = total_words // len(app.articles) if app.articles else 0
            st.metric("Слов на статью", avg_words)
        with col4:
            categories = set(article.get('category', 'unknown') for article in app.articles)
            st.metric("Категорий", len(categories))
        
        # Вкладки
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📄 Данные", "🔧 Предобработка", "✂️ Токенизация", 
            "🧩 Подсловные модели", "📊 Анализ", "📈 Визуализация"
        ])
        
        with tab1:
            st.header("Загруженные данные")
            
            # Просмотр статей
            if st.checkbox("Показать статьи"):
                for i, article in enumerate(app.articles[:5]):  # Показываем первые 5
                    with st.expander(f"Статья {i+1}: {article['title'][:50]}..."):
                        st.write(f"**Заголовок:** {article['title']}")
                        st.write(f"**Категория:** {article.get('category', 'Не указана')}")
                        st.write(f"**Дата:** {article.get('date', 'Не указана')}")
                        st.write(f"**Текст:** {article['text'][:500]}...")
                        if article.get('url'):
                            st.write(f"**URL:** {article['url']}")
        
        with tab2:
            st.header("Предобработка текста")
            
            if st.button("🔄 Предобработать тексты"):
                # Создание конфигурации
                config = PreprocessingConfig(
                    replace_numbers=replace_numbers,
                    replace_urls=replace_urls,
                    replace_emails=replace_emails,
                    replace_phones=replace_phones,
                    replace_dates=replace_dates,
                    replace_times=replace_times,
                    replace_currencies=replace_currencies,
                    normalize_punctuation=normalize_punctuation,
                    normalize_quotes=normalize_quotes,
                    normalize_dashes=normalize_dashes,
                    normalize_spaces=normalize_spaces,
                    expand_abbreviations=expand_abbreviations,
                    to_lowercase=to_lowercase
                )
                
                with st.spinner("Предобработка текстов..."):
                    app.processed_articles = app.preprocess_articles(config)
                
                if app.processed_articles:
                    st.success(f"Предобработано {len(app.processed_articles)} статей")
                    
                    # Показать пример
                    if app.processed_articles:
                        st.subheader("Пример предобработки")
                        original = app.articles[0]['text'][:300]
                        processed = app.processed_articles[0]['text'][:300]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Исходный текст:**")
                            st.text(original)
                        with col2:
                            st.write("**Обработанный текст:**")
                            st.text(processed)
        
        with tab3:
            st.header("Анализ токенизации")
            
            if st.button("🔄 Анализировать токенизацию"):
                texts = [article['text'] for article in app.articles]
                
                with st.spinner("Анализ токенизации..."):
                    app.analysis_results = app.analyze_tokenization(texts)
                
                if app.analysis_results:
                    st.success("Анализ токенизации завершен")
                    
                    # Результаты сравнения
                    if 'comparison' in app.analysis_results:
                        comparison_data = []
                        for method, metrics in app.analysis_results['comparison'].items():
                            comparison_data.append({
                                'Метод': method,
                                'Размер словаря (train)': metrics['train_vocab_size'],
                                'Размер словаря (test)': metrics['test_vocab_size'],
                                'OOV Rate': f"{metrics['oov_rate']:.4f}",
                                'Семантическое сходство': f"{metrics['semantic_similarity']:.4f}",
                                'Время обработки (с)': f"{metrics['train_processing_time']:.4f}"
                            })
                        
                        df = pd.DataFrame(comparison_data)
                        st.dataframe(df, use_container_width=True)
        
        with tab4:
            st.header("Подсловные модели")
            
            if st.button("🔄 Обучить подсловные модели"):
                texts = [article['text'] for article in app.articles]
                
                with st.spinner("Обучение подсловных моделей..."):
                    subword_results = app.train_subword_models(texts, vocab_sizes)
                
                if subword_results and 'evaluation_results' in subword_results:
                    st.success("Обучение подсловных моделей завершено")
                    
                    # Результаты оценки
                    eval_data = []
                    for model_name, metrics in subword_results['evaluation_results'].items():
                        eval_data.append({
                            'Модель': model_name,
                            'Коэффициент фрагментации': f"{metrics['fragmentation_rate']:.4f}",
                            'Коэффициент сжатия': f"{metrics['compression_ratio']:.4f}",
                            'Время обработки (с)': f"{metrics['avg_processing_time']:.4f}",
                            'Токенов в секунду': f"{metrics['tokens_per_second']:.2f}"
                        })
                    
                    df = pd.DataFrame(eval_data)
                    st.dataframe(df, use_container_width=True)
        
        with tab5:
            st.header("Статистический анализ")
            
            if app.articles:
                # Анализ длины текстов
                text_lengths = [len(article['text'].split()) for article in app.articles]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Распределение длины текстов")
                    fig = px.histogram(
                        x=text_lengths,
                        nbins=20,
                        title="Распределение количества слов в статьях"
                    )
                    fig.update_layout(
                        xaxis_title="Количество слов",
                        yaxis_title="Количество статей"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Статистики длины текстов")
                    stats_data = {
                        'Метрика': ['Среднее', 'Медиана', 'Стандартное отклонение', 'Минимум', 'Максимум'],
                        'Значение': [
                            f"{np.mean(text_lengths):.1f}",
                            f"{np.median(text_lengths):.1f}",
                            f"{np.std(text_lengths):.1f}",
                            f"{min(text_lengths)}",
                            f"{max(text_lengths)}"
                        ]
                    }
                    st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
                
                # Анализ по категориям
                if any(article.get('category') for article in app.articles):
                    st.subheader("Анализ по категориям")
                    
                    category_stats = {}
                    for article in app.articles:
                        category = article.get('category', 'unknown')
                        if category not in category_stats:
                            category_stats[category] = []
                        category_stats[category].append(len(article['text'].split()))
                    
                    category_data = []
                    for category, lengths in category_stats.items():
                        category_data.append({
                            'Категория': category,
                            'Количество статей': len(lengths),
                            'Средняя длина': f"{np.mean(lengths):.1f}",
                            'Общее количество слов': sum(lengths)
                        })
                    
                    df_categories = pd.DataFrame(category_data)
                    st.dataframe(df_categories, use_container_width=True)
        
        with tab6:
            st.header("Визуализация результатов")
            
            if app.analysis_results and 'comparison' in app.analysis_results:
                # График OOV Rate
                comparison_data = app.analysis_results['comparison']
                methods = list(comparison_data.keys())
                oov_rates = [comparison_data[method]['oov_rate'] for method in methods]
                
                fig = px.bar(
                    x=methods,
                    y=oov_rates,
                    title="Сравнение OOV Rate по методам токенизации"
                )
                fig.update_layout(
                    xaxis_title="Метод токенизации",
                    yaxis_title="OOV Rate"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # График времени обработки
                processing_times = [comparison_data[method]['train_processing_time'] for method in methods]
                
                fig2 = px.bar(
                    x=methods,
                    y=processing_times,
                    title="Время обработки по методам токенизации"
                )
                fig2.update_layout(
                    xaxis_title="Метод токенизации",
                    yaxis_title="Время обработки (секунды)"
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        # Экспорт результатов
        st.header("📤 Экспорт результатов")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Сохранить обработанные данные"):
                if app.processed_articles:
                    # Сохранение в JSONL
                    jsonl_data = '\n'.join(json.dumps(article, ensure_ascii=False) for article in app.processed_articles)
                    st.download_button(
                        label="📄 Скачать JSONL",
                        data=jsonl_data,
                        file_name=f"processed_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
                        mime="text/plain"
                    )
        
        with col2:
            if st.button("📊 Сохранить результаты анализа"):
                if app.analysis_results:
                    analysis_json = json.dumps(app.analysis_results, ensure_ascii=False, indent=2, default=str)
                    st.download_button(
                        label="📈 Скачать анализ",
                        data=analysis_json,
                        file_name=f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        with col3:
            if st.button("📋 Создать отчет"):
                # Создание HTML отчета
                report_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Отчет анализа текстов</title>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        h1, h2 {{ color: #333; }}
                        .section {{ margin-bottom: 30px; }}
                        .stats {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h1>Отчет анализа текстов и токенизации</h1>
                    <p><strong>Дата создания:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <div class="section">
                        <h2>Общая информация</h2>
                        <div class="stats">
                            <p><strong>Количество статей:</strong> {len(app.articles)}</p>
                            <p><strong>Общее количество слов:</strong> {sum(len(article['text'].split()) for article in app.articles):,}</p>
                            <p><strong>Среднее количество слов на статью:</strong> {sum(len(article['text'].split()) for article in app.articles) // len(app.articles) if app.articles else 0:,}</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                st.download_button(
                    label="📄 Скачать отчет",
                    data=report_html,
                    file_name=f"text_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )

if __name__ == "__main__":
    main()
