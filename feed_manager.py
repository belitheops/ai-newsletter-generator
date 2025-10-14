import json
import os
from typing import List, Dict, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedManager:
    def __init__(self, feeds_file: str = "feeds.json"):
        self.feeds_file = feeds_file
        self.feeds = self._load_feeds()
    
    def _load_feeds(self) -> List[Dict]:
        """Load feeds from JSON file"""
        try:
            if os.path.exists(self.feeds_file):
                with open(self.feeds_file, 'r', encoding='utf-8') as f:
                    feeds = json.load(f)
                    if isinstance(feeds, list):
                        return feeds
                    else:
                        logger.warning(f"Invalid feeds format, starting fresh")
                        return []
            else:
                logger.info(f"Feeds file not found, starting fresh")
                return []
        except Exception as e:
            logger.error(f"Error loading feeds: {e}")
            return []
    
    def _save_feeds(self):
        """Save feeds to JSON file"""
        try:
            # Create backup
            if os.path.exists(self.feeds_file):
                backup_file = f"{self.feeds_file}.backup"
                with open(self.feeds_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            
            # Save current feeds
            with open(self.feeds_file, 'w', encoding='utf-8') as f:
                json.dump(self.feeds, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Feeds saved successfully: {len(self.feeds)} feeds")
        except Exception as e:
            logger.error(f"Error saving feeds: {e}")
    
    def get_all_feeds(self) -> List[Dict]:
        """Get all feeds"""
        return self.feeds
    
    def get_enabled_feeds(self) -> List[Dict]:
        """Get only enabled feeds"""
        return [feed for feed in self.feeds if feed.get('enabled', True)]
    
    def get_feed_by_id(self, feed_id: str) -> Optional[Dict]:
        """Get a specific feed by ID"""
        for feed in self.feeds:
            if feed.get('id') == feed_id:
                return feed
        return None
    
    def add_feed(self, name: str, url: str, category: str = "Other", enabled: bool = True) -> bool:
        """Add a new RSS feed"""
        try:
            # Generate ID from name
            feed_id = name.lower().replace(' ', '_').replace('-', '_')
            
            # Check if ID already exists
            if self.get_feed_by_id(feed_id):
                logger.warning(f"Feed with ID {feed_id} already exists")
                return False
            
            # Create new feed
            new_feed = {
                'id': feed_id,
                'name': name,
                'url': url,
                'type': 'rss',
                'enabled': enabled,
                'category': category,
                'added_at': datetime.now().isoformat()
            }
            
            self.feeds.append(new_feed)
            self._save_feeds()
            logger.info(f"Added new feed: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding feed: {e}")
            return False
    
    def update_feed(self, feed_id: str, **kwargs) -> bool:
        """Update an existing feed"""
        try:
            for feed in self.feeds:
                if feed.get('id') == feed_id:
                    # Update allowed fields
                    allowed_fields = ['name', 'url', 'enabled', 'category']
                    for key, value in kwargs.items():
                        if key in allowed_fields:
                            feed[key] = value
                    
                    feed['updated_at'] = datetime.now().isoformat()
                    self._save_feeds()
                    logger.info(f"Updated feed: {feed_id}")
                    return True
            
            logger.warning(f"Feed not found: {feed_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error updating feed: {e}")
            return False
    
    def delete_feed(self, feed_id: str) -> bool:
        """Delete a feed"""
        try:
            original_count = len(self.feeds)
            self.feeds = [feed for feed in self.feeds if feed.get('id') != feed_id]
            
            if len(self.feeds) < original_count:
                self._save_feeds()
                logger.info(f"Deleted feed: {feed_id}")
                return True
            else:
                logger.warning(f"Feed not found: {feed_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting feed: {e}")
            return False
    
    def toggle_feed(self, feed_id: str) -> bool:
        """Toggle feed enabled/disabled status"""
        try:
            for feed in self.feeds:
                if feed.get('id') == feed_id:
                    feed['enabled'] = not feed.get('enabled', True)
                    self._save_feeds()
                    logger.info(f"Toggled feed {feed_id}: enabled={feed['enabled']}")
                    return True
            
            logger.warning(f"Feed not found: {feed_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error toggling feed: {e}")
            return False
    
    def get_feeds_by_category(self, category: str) -> List[Dict]:
        """Get feeds by category"""
        return [feed for feed in self.feeds if feed.get('category') == category]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        categories = set()
        for feed in self.feeds:
            if 'category' in feed:
                categories.add(feed['category'])
        return sorted(list(categories))
