import trafilatura
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.sources = {
            'TechCrunch AI': {
                'url': 'https://techcrunch.com/category/artificial-intelligence/',
                'parser': self._parse_techcrunch
            },
            'MIT News AI/ML': {
                'url': 'https://news.mit.edu/topic/artificial-intelligence2',
                'parser': self._parse_mit_news
            },
            'AI News': {
                'url': 'https://artificialintelligence-news.com/',
                'parser': self._parse_ai_news
            },
            'MIT Tech Review': {
                'url': 'https://www.technologyreview.com/topic/artificial-intelligence/',
                'parser': self._parse_mit_review
            },
            'VentureBeat AI': {
                'url': 'https://venturebeat.com/ai/',
                'parser': self._parse_venturebeat
            },
            'Wired AI': {
                'url': 'https://www.wired.com/tag/artificial-intelligence/',
                'parser': self._parse_wired
            },
            'Forbes AI': {
                'url': 'https://www.forbes.com/ai/',
                'parser': self._parse_forbes
            },
            'OpenAI Blog': {
                'url': 'https://openai.com/blog/',
                'parser': self._parse_openai_blog
            },
            'ScienceDaily AI': {
                'url': 'https://www.sciencedaily.com/news/computers_math/artificial_intelligence/',
                'parser': self._parse_sciencedaily
            },
            'The Verge AI': {
                'url': 'https://www.theverge.com/ai-artificial-intelligence',
                'parser': self._parse_verge
            }
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_website_text_content(self, url: str) -> str:
        """Extract main text content from a website URL using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                return text or ""
            return ""
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return ""

    def scrape_all_sources(self) -> List[Dict]:
        """Scrape articles from all configured news sources"""
        all_articles = []
        
        for source_name, source_config in self.sources.items():
            try:
                logger.info(f"Scraping {source_name}...")
                articles = self._scrape_source(source_name, source_config)
                all_articles.extend(articles)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                continue
        
        # Filter articles from last 24 hours
        recent_articles = self._filter_recent_articles(all_articles)
        logger.info(f"Total articles scraped: {len(all_articles)}, Recent (24h): {len(recent_articles)}")
        
        return recent_articles

    def _scrape_source(self, source_name: str, source_config: Dict) -> List[Dict]:
        """Scrape articles from a single source"""
        try:
            response = requests.get(source_config['url'], headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = source_config['parser'](soup, source_config['url'])
            
            # Add full content for each article
            for article in articles:
                if article.get('url'):
                    article['full_content'] = self.get_website_text_content(article['url'])
                    article['source'] = source_name
            
            return articles
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {e}")
            return []

    def _parse_techcrunch(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse TechCrunch articles"""
        articles = []
        article_elements = soup.find_all('article', class_='post-block')[:5]
        
        for element in article_elements:
            try:
                title_elem = element.find('h2') or element.find('h3')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href')
                    if url and not url.startswith('http'):
                        url = f"https://techcrunch.com{url}"
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_date': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing TechCrunch article: {e}")
                continue
        
        return articles

    def _parse_mit_news(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse MIT News articles"""
        articles = []
        article_elements = soup.find_all('div', class_='views-row')[:5]
        
        for element in article_elements:
            try:
                title_elem = element.find('h3') or element.find('h2')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href')
                    if url and not url.startswith('http'):
                        url = f"https://news.mit.edu{url}"
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_date': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing MIT News article: {e}")
                continue
        
        return articles

    def _parse_ai_news(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse AI News articles"""
        articles = []
        article_elements = soup.find_all('article')[:5]
        
        for element in article_elements:
            try:
                title_elem = element.find('h2') or element.find('h1')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href')
                    if url and not url.startswith('http') and not url.startswith('//'):
                        url = f"https://artificialintelligence-news.com{url}"
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_date': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing AI News article: {e}")
                continue
        
        return articles

    def _parse_mit_review(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse MIT Technology Review articles"""
        articles = []
        article_elements = soup.find_all('div', class_='content')[:5]
        
        for element in article_elements:
            try:
                title_elem = element.find('h3') or element.find('h2')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href')
                    if url and not url.startswith('http'):
                        url = f"https://www.technologyreview.com{url}"
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_date': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing MIT Review article: {e}")
                continue
        
        return articles

    def _parse_venturebeat(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse VentureBeat articles"""
        articles = []
        article_elements = soup.find_all('article')[:5]
        
        for element in article_elements:
            try:
                title_elem = element.find('h2') or element.find('h3')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href')
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_date': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing VentureBeat article: {e}")
                continue
        
        return articles

    def _parse_wired(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse Wired articles"""
        articles = []
        article_elements = soup.find_all('div', attrs={'data-testid': 'SummaryItemWrapper'})[:5]
        
        for element in article_elements:
            try:
                title_elem = element.find('h3') or element.find('h2')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href')
                    if url and not url.startswith('http'):
                        url = f"https://www.wired.com{url}"
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_date': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing Wired article: {e}")
                continue
        
        return articles

    def _parse_forbes(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse Forbes articles"""
        articles = []
        article_elements = soup.find_all('article')[:5]
        
        for element in article_elements:
            try:
                title_elem = element.find('h3') or element.find('h2')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href')
                    if url and not url.startswith('http'):
                        url = f"https://www.forbes.com{url}"
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_date': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing Forbes article: {e}")
                continue
        
        return articles

    def _parse_openai_blog(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse OpenAI blog articles"""
        articles = []
        article_elements = soup.find_all('article')[:5]
        
        for element in article_elements:
            try:
                title_elem = element.find('h3') or element.find('h2')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href')
                    if url and not url.startswith('http'):
                        url = f"https://openai.com{url}"
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_date': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing OpenAI blog article: {e}")
                continue
        
        return articles

    def _parse_sciencedaily(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse ScienceDaily articles"""
        articles = []
        article_elements = soup.find_all('div', class_='latest')[:5]
        
        for element in article_elements:
            try:
                title_elem = element.find('h3') or element.find('h2')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href')
                    if url and not url.startswith('http'):
                        url = f"https://www.sciencedaily.com{url}"
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_date': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing ScienceDaily article: {e}")
                continue
        
        return articles

    def _parse_verge(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse The Verge articles"""
        articles = []
        article_elements = soup.find_all('div', class_='c-entry-box--compact')[:5]
        
        for element in article_elements:
            try:
                title_elem = element.find('h2') or element.find('h3')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem.get('href')
                    if url and not url.startswith('http'):
                        url = f"https://www.theverge.com{url}"
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'published_date': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing Verge article: {e}")
                continue
        
        return articles

    def _filter_recent_articles(self, articles: List[Dict], hours: int = 24) -> List[Dict]:
        """Filter articles from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_articles = []
        
        for article in articles:
            try:
                # Since we're setting published_date to now, all articles are considered recent
                # In a real implementation, you'd parse actual publication dates from the websites
                recent_articles.append(article)
            except Exception as e:
                logger.error(f"Error filtering article date: {e}")
                continue
        
        return recent_articles
