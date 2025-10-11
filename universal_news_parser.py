import os
os.environ['TCL_LIBRARY'] = "C:/Program Files/Python313/tcl/tcl8.6"
os.environ['TK_LIBRARY'] = "C:/Program Files/Python313/tcl/tk8.6"
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict, Optional
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalNewsParser:
    """Универсальный парсер новостных сайтов"""
    
    def __init__(self, delay=1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Конфигурация для разных сайтов
        self.site_configs = {
            'kommersant.ru': {
                'base_url': 'https://www.kommersant.ru',
                'article_patterns': [
                    r'/doc/\d+',
                ],
                'title_selectors': [
                    'h1.doc_header_title',
                    'h1.doc_header__title',
                    'h1[class*="title"]',
                    'h1'
                ],
                'text_selectors': [
                    '.doc_text',
                    '.doc_text__content',
                    '.article__text',
                    '.article__body'
                ],
                'date_selectors': [
                    '.doc_header_date',
                    'meta[property="article:published_time"]',
                    'time[datetime]'
                ],
                'category_selectors': [
                    '.doc_header_section',
                    'meta[property="article:section"]'
                ],
                'categories': {
                    'politics': '/politics/',
                    'economy': '/economy/',
                    'society': '/society/',
                    'world': '/world/',
                    'sport': '/sport/',
                    'culture': '/culture/',
                    'business': '/business/',
                    'finance': '/finance/'
                }
            }
        }
    
    def parse_site(self, site_name: str, max_articles_per_category: int = 50) -> List[Dict]:
        """Парсинг конкретного сайта"""
        if site_name not in self.site_configs:
            logger.error(f"Неизвестный сайт: {site_name}")
            return []
        
        config = self.site_configs[site_name]
        logger.info(f"Начинаем парсинг сайта: {site_name}")
        
        all_articles = []
        
        for category_name, category_path in config['categories'].items():
            logger.info(f"Парсим категорию: {category_name}")
            category_url = config['base_url'] + category_path
            
            # Получение ссылок на статьи
            article_links = self._get_article_links(category_url, config, max_pages=5)
            logger.info(f"Найдено {len(article_links)} ссылок в категории {category_name}")
            
            # Ограничение количества статей
            if len(article_links) > max_articles_per_category:
                article_links = article_links[:max_articles_per_category]
            
            # Парсинг статей
            for i, link in enumerate(article_links, 1):
                logger.info(f"Парсим статью {i}/{len(article_links)} из {category_name}")
                article = self._parse_article(link, config, site_name)
                if article:
                    article['category'] = category_name
                    all_articles.append(article)
                
                time.sleep(self.delay)
        
        logger.info(f"Успешно спарсено {len(all_articles)} статей с сайта {site_name}")
        return all_articles
    
    def _get_article_links(self, category_url: str, config: Dict, max_pages: int = 5) -> List[str]:
        """Получение ссылок на статьи из категории"""
        article_links = []
        
        for page in range(1, max_pages + 1):
            try:
                if page == 1:
                    url = category_url
                else:
                    url = f"{category_url}?page={page}"
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Поиск ссылок на статьи
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    if href and self._is_article_link(href, config):
                        full_url = urljoin(config['base_url'], href)
                        if full_url not in article_links:
                            article_links.append(full_url)
                
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Ошибка при обработке страницы {page}: {e}")
                continue
        
        return article_links
    
    def _is_article_link(self, href: str, config: Dict) -> bool:
        """Проверка, является ли ссылка ссылкой на статью"""
        for pattern in config['article_patterns']:
            if re.search(pattern, href):
                return True
        return False
    
    def _parse_article(self, url: str, config: Dict, site_name: str) -> Optional[Dict]:
        """Парсинг отдельной статьи"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Извлечение заголовка
            title = self._extract_title(soup, config)
            if not title:
                return None
            
            # Извлечение текста статьи
            text = self._extract_text(soup, config)
            if not text or len(text.strip()) < 100:
                return None
            
            # Извлечение даты
            date = self._extract_date(soup, config, url)
            
            # Извлечение тегов
            tags = self._extract_tags(soup)
            
            # Извлечение автора
            author = self._extract_author(soup)
            
            article_data = {
                'title': title.strip(),
                'text': text.strip(),
                'date': date,
                'url': url,
                'tags': tags,
                'author': author,
                'source': site_name,
                'parsed_at': datetime.now().isoformat()
            }
            
            return article_data
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге статьи {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup, config: Dict) -> Optional[str]:
        """Извлечение заголовка статьи"""
        for selector in config['title_selectors']:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                return title_elem.get_text().strip()
        return None
    
    def _extract_text(self, soup: BeautifulSoup, config: Dict) -> Optional[str]:
        """Извлечение основного текста статьи"""
        # Удаление ненужных элементов
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement', 'ad']):
            element.decompose()
        
        text_parts = []
        
        for selector in config['text_selectors']:
            text_elem = soup.select_one(selector)
            if text_elem:
                paragraphs = text_elem.find_all(['p', 'div'], recursive=True)
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text and len(text) > 20:
                        text_parts.append(text)
                break
        
        if not text_parts:
            # Fallback: поиск по всему документу
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 50:
                    text_parts.append(text)
        
        return ' '.join(text_parts) if text_parts else None
    
    def _extract_date(self, soup: BeautifulSoup, config: Dict, url: str) -> Optional[str]:
        """Извлечение даты публикации"""
        for selector in config['date_selectors']:
            elem = soup.select_one(selector)
            if elem:
                date_str = elem.get('content') or elem.get('datetime') or elem.get_text()
                if date_str:
                    try:
                        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        return parsed_date.isoformat()
                    except:
                        continue
        
        # Извлечение даты из URL
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if date_match:
            try:
                year, month, day = date_match.groups()
                parsed_date = datetime(int(year), int(month), int(day))
                return parsed_date.isoformat()
            except:
                pass
        
        return None
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Извлечение тегов статьи"""
        tags = []
        
        tag_selectors = [
            '.tags a',
            '.article__tags a',
            '.article__keywords a',
            'meta[name="keywords"]'
        ]
        
        for selector in tag_selectors:
            if selector.startswith('meta'):
                elem = soup.select_one(selector)
                if elem:
                    content = elem.get('content', '')
                    if content:
                        tags.extend([tag.strip() for tag in content.split(',')])
            else:
                elems = soup.select(selector)
                for elem in elems:
                    tag = elem.get_text().strip()
                    if tag:
                        tags.append(tag)
        
        return list(set(tags))
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Извлечение автора статьи"""
        author_selectors = [
            '.author',
            '.article__author',
            'meta[name="author"]',
            'meta[property="article:author"]'
        ]
        
        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem:
                author = elem.get('content') or elem.get_text()
                if author and author.strip():
                    return author.strip()
        
        return None
    
    def parse_all_sites(self, max_articles_per_category: int = 30) -> List[Dict]:
        """Парсинг всех доступных сайтов (только Коммерсант)"""
        all_articles = []
        
        try:
            articles = self.parse_site('kommersant.ru', max_articles_per_category)
            all_articles.extend(articles)
            logger.info(f"Всего статей собрано: {len(all_articles)}")
        except Exception as e:
            logger.error(f"Ошибка при парсинге сайта kommersant.ru: {e}")
        
        return all_articles
    
    def save_articles(self, articles: List[Dict], filename: str = "news_articles.jsonl"):
        """Сохранение статей в JSONL формате"""
        # Определяем путь относительно текущего файла
        current_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(current_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for article in articles:
                f.write(json.dumps(article, ensure_ascii=False) + '\n')
        
        logger.info(f"Сохранено {len(articles)} статей в файл {filepath}")
        return filepath

def main():
    """Основная функция для запуска парсера"""
    parser = UniversalNewsParser(delay=1.0)
    
    # Парсинг всех сайтов
    logger.info("Начинаем парсинг новостных сайтов")
    articles = parser.parse_all_sites(max_articles_per_category=20)
    
    if articles:
        # Сохранение результатов
        filepath = parser.save_articles(articles)
        
        # Статистика
        total_words = sum(len(article['text'].split()) for article in articles)
        sources = {}
        for article in articles:
            source = article['source']
            sources[source] = sources.get(source, 0) + 1
        
        logger.info(f"Парсинг завершен!")
        logger.info(f"Всего статей: {len(articles)}")
        logger.info(f"Всего слов: {total_words:,}")
        logger.info(f"Среднее количество слов на статью: {total_words // len(articles):,}")
        logger.info(f"Статьи по источникам:")
        for source, count in sources.items():
            logger.info(f"  {source}: {count} статей")
        logger.info(f"Результаты сохранены в: {filepath}")
    else:
        logger.error("Не удалось спарсить ни одной статьи")

if __name__ == "__main__":
    main()
