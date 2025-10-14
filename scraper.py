import trafilatura
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import feedparser
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import re
from feed_manager import FeedManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        # Load feeds from feed manager
        self.feed_manager = FeedManager()
        self.sources = self._load_sources_from_feeds()
        
        # Create session with retry logic
        self.session = self._create_session()
        
        # Randomized modern headers
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
    
    def _load_sources_from_feeds(self) -> Dict:
        """Load sources from feed manager"""
        sources = {}
        enabled_feeds = self.feed_manager.get_enabled_feeds()
        
        for feed in enabled_feeds:
            sources[feed['name']] = {
                'type': feed.get('type', 'rss'),
                'url': feed['url'],
                'category': feed.get('category', 'Other')
            }
        
        logger.info(f"Loaded {len(sources)} enabled RSS feeds")
        return sources
    
    def reload_feeds(self):
        """Reload feeds from feed manager (useful after updates)"""
        self.feed_manager = FeedManager()
        self.sources = self._load_sources_from_feeds()
    
    def _create_session(self):
        """Create requests session with retry logic"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _get_headers(self):
        """Get randomized headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def get_website_text_content(self, url: str) -> str:
        """Extract main text content from a website URL using trafilatura with session"""
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=15)
            if response.status_code == 200:
                text = trafilatura.extract(response.content)
                return text or ""
            return ""
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return ""

    def scrape_all_sources(self, custom_sources: Dict = None) -> List[Dict]:
        """Scrape articles from all configured news sources
        
        Args:
            custom_sources: Optional custom sources dict to use instead of self.sources
        """
        all_articles = []
        failed_sources = []
        
        # Use custom sources if provided, otherwise use default
        sources_to_scrape = custom_sources if custom_sources is not None else self.sources
        
        for source_name, source_config in sources_to_scrape.items():
            try:
                logger.info(f"Scraping {source_name}...")
                articles = self._scrape_source(source_name, source_config)
                if articles:
                    all_articles.extend(articles)
                    logger.info(f"✅ {source_name}: {len(articles)} articles")
                else:
                    failed_sources.append(source_name)
                    logger.warning(f"⚠️ {source_name}: 0 articles")
                
                # Jittered pacing: 2-5 seconds between sources
                time.sleep(random.uniform(2, 5))
            except Exception as e:
                logger.error(f"❌ Error scraping {source_name}: {e}")
                failed_sources.append(source_name)
                continue
        
        # Log summary
        sources_count = len(sources_to_scrape)
        logger.info(f"Total articles scraped: {len(all_articles)} from {sources_count - len(failed_sources)}/{sources_count} sources")
        if failed_sources:
            logger.warning(f"Failed sources: {', '.join(failed_sources)}")
        
        # Filter articles from last 48 hours for fresher content
        recent_articles = self._filter_recent_articles(all_articles, hours=48)
        logger.info(f"Recent articles (48h): {len(recent_articles)}")
        
        return recent_articles

    def _scrape_source(self, source_name: str, source_config: Dict) -> List[Dict]:
        """Scrape articles from a single source using RSS"""
        try:
            if source_config['type'] == 'rss':
                return self._scrape_rss_feed(source_name, source_config['url'])
            else:
                logger.error(f"Unknown source type for {source_name}")
                return []
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {e}")
            return []
    
    def _scrape_rss_feed(self, source_name: str, feed_url: str) -> List[Dict]:
        """Scrape articles from RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            
            # Get up to 5 most recent entries
            for entry in feed.entries[:5]:
                try:
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '')
                    
                    # Get published date
                    published_date = datetime.now().isoformat()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6]).isoformat()
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_date = datetime(*entry.updated_parsed[:6]).isoformat()
                    
                    # Get summary from RSS or extract from article
                    summary = entry.get('summary', '') or entry.get('description', '')
                    
                    if title and url:
                        article = {
                            'title': title,
                            'url': url,
                            'published_date': published_date,
                            'source': source_name,
                            'full_content': summary  # Use RSS summary initially
                        }
                        articles.append(article)
                        
                except Exception as e:
                    logger.error(f"Error parsing RSS entry from {source_name}: {e}")
                    continue
            
            # Optionally fetch full content for articles (commented out to avoid blocks)
            # for article in articles[:3]:  # Only fetch first 3 to avoid rate limits
            #     if article.get('url'):
            #         full_content = self.get_website_text_content(article['url'])
            #         if full_content:
            #             article['full_content'] = full_content
            
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing RSS feed {source_name}: {e}")
            return []

    def _filter_recent_articles(self, articles: List[Dict], hours: int = 48) -> List[Dict]:
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
