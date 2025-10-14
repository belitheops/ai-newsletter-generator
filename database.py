import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsletterDatabase:
    def __init__(self, db_file: str = "newsletters.json"):
        self.db_file = db_file
        self.newsletters = self._load_database()

    def _load_database(self) -> List[Dict]:
        """Load newsletters from JSON file"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'newsletters' in data:
                        return data['newsletters']
                    else:
                        logger.warning(f"Invalid database format in {self.db_file}, starting fresh")
                        return []
            else:
                logger.info(f"Database file {self.db_file} not found, starting fresh")
                return []
        except Exception as e:
            logger.error(f"Error loading database: {e}, starting with empty database")
            return []

    def _save_database(self):
        """Save newsletters to JSON file"""
        try:
            # Create backup before saving
            if os.path.exists(self.db_file):
                backup_file = f"{self.db_file}.backup"
                with open(self.db_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            
            # Save current data
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.newsletters, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"Database saved successfully with {len(self.newsletters)} newsletters")
            
        except Exception as e:
            logger.error(f"Error saving database: {e}")

    def save_newsletter(self, newsletter_data: Dict) -> str:
        """Save a newsletter and return its ID"""
        try:
            # Generate unique ID based on timestamp
            newsletter_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            
            # Add metadata
            newsletter = {
                'id': newsletter_id,
                'title': newsletter_data.get('title', ''),
                'html_content': newsletter_data.get('html_content', ''),
                'markdown_content': newsletter_data.get('markdown_content', ''),
                'story_count': newsletter_data.get('story_count', 0),
                'created_at': newsletter_data.get('created_at', datetime.now().isoformat()),
                'generation_method': newsletter_data.get('generation_method', 'manual'),
                'config_id': newsletter_data.get('config_id', None),
                'config_name': newsletter_data.get('config_name', None),
                'email_sent': False,
                'email_sent_at': None,
                'error_reason': newsletter_data.get('error_reason', None)
            }
            
            # Add to newsletters list
            self.newsletters.append(newsletter)
            
            # Save to file
            self._save_database()
            
            logger.info(f"Newsletter saved with ID: {newsletter_id}")
            return newsletter_id
            
        except Exception as e:
            logger.error(f"Error saving newsletter: {e}")
            return ""

    def get_newsletter(self, newsletter_id: str) -> Optional[Dict]:
        """Get a specific newsletter by ID"""
        for newsletter in self.newsletters:
            if newsletter.get('id') == newsletter_id:
                return newsletter
        return None

    def get_all_newsletters(self) -> List[Dict]:
        """Get all newsletters, sorted by creation date (newest first)"""
        try:
            # Sort by created_at in descending order
            sorted_newsletters = sorted(
                self.newsletters, 
                key=lambda x: x.get('created_at', ''), 
                reverse=True
            )
            return sorted_newsletters
        except Exception as e:
            logger.error(f"Error retrieving newsletters: {e}")
            return self.newsletters

    def get_recent_newsletters(self, limit: int = 10) -> List[Dict]:
        """Get recent newsletters with limit"""
        all_newsletters = self.get_all_newsletters()
        return all_newsletters[:limit]

    def mark_newsletter_sent(self, newsletter_id: str) -> bool:
        """Mark a newsletter as sent via email"""
        try:
            for newsletter in self.newsletters:
                if newsletter.get('id') == newsletter_id:
                    newsletter['email_sent'] = True
                    newsletter['email_sent_at'] = datetime.now().isoformat()
                    self._save_database()
                    logger.info(f"Newsletter {newsletter_id} marked as sent")
                    return True
            
            logger.warning(f"Newsletter {newsletter_id} not found for marking as sent")
            return False
            
        except Exception as e:
            logger.error(f"Error marking newsletter as sent: {e}")
            return False

    def delete_newsletter(self, newsletter_id: str) -> bool:
        """Delete a newsletter"""
        try:
            original_count = len(self.newsletters)
            self.newsletters = [n for n in self.newsletters if n.get('id') != newsletter_id]
            
            if len(self.newsletters) < original_count:
                self._save_database()
                logger.info(f"Newsletter {newsletter_id} deleted")
                return True
            else:
                logger.warning(f"Newsletter {newsletter_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting newsletter: {e}")
            return False

    def get_newsletters_by_date(self, date_str: str) -> List[Dict]:
        """Get newsletters created on a specific date (YYYY-MM-DD)"""
        try:
            newsletters_on_date = []
            for newsletter in self.newsletters:
                created_at = newsletter.get('created_at', '')
                if created_at.startswith(date_str):
                    newsletters_on_date.append(newsletter)
            
            return sorted(newsletters_on_date, key=lambda x: x.get('created_at', ''), reverse=True)
        except Exception as e:
            logger.error(f"Error getting newsletters by date: {e}")
            return []

    def get_sent_newsletters(self) -> List[Dict]:
        """Get all newsletters that were sent via email"""
        try:
            sent_newsletters = [n for n in self.newsletters if n.get('email_sent', False)]
            return sorted(sent_newsletters, key=lambda x: x.get('email_sent_at', ''), reverse=True)
        except Exception as e:
            logger.error(f"Error getting sent newsletters: {e}")
            return []

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            total_newsletters = len(self.newsletters)
            sent_newsletters = len(self.get_sent_newsletters())
            
            # Count by generation method
            manual_count = len([n for n in self.newsletters if n.get('generation_method') == 'manual'])
            scheduled_count = len([n for n in self.newsletters if n.get('generation_method') == 'scheduled'])
            
            # Count error newsletters
            error_count = len([n for n in self.newsletters if n.get('error_reason')])
            
            # Get date range
            if self.newsletters:
                dates = [n.get('created_at', '') for n in self.newsletters if n.get('created_at')]
                earliest = min(dates) if dates else None
                latest = max(dates) if dates else None
            else:
                earliest = latest = None
            
            return {
                'total_newsletters': total_newsletters,
                'sent_newsletters': sent_newsletters,
                'unsent_newsletters': total_newsletters - sent_newsletters,
                'manual_generation': manual_count,
                'scheduled_generation': scheduled_count,
                'error_newsletters': error_count,
                'earliest_newsletter': earliest,
                'latest_newsletter': latest,
                'database_file': self.db_file,
                'database_size_kb': round(os.path.getsize(self.db_file) / 1024, 2) if os.path.exists(self.db_file) else 0
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

    def cleanup_old_newsletters(self, days_to_keep: int = 30) -> int:
        """Remove newsletters older than specified days"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.isoformat()
            
            original_count = len(self.newsletters)
            self.newsletters = [
                n for n in self.newsletters 
                if n.get('created_at', '') >= cutoff_str
            ]
            
            removed_count = original_count - len(self.newsletters)
            
            if removed_count > 0:
                self._save_database()
                logger.info(f"Cleaned up {removed_count} old newsletters")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0

    def export_newsletters(self, export_file: str) -> bool:
        """Export all newsletters to a JSON file"""
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'total_newsletters': len(self.newsletters),
                'newsletters': self.newsletters
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Newsletters exported to {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting newsletters: {e}")
            return False
