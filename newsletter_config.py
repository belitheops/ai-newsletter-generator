import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsletterConfigManager:
    def __init__(self, config_file: str = "newsletter_configs.json"):
        self.config_file = config_file
        self.configs = self._load_configs()
    
    def _load_configs(self) -> List[Dict]:
        """Load newsletter configurations from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    configs = json.load(f)
                    if isinstance(configs, list):
                        return configs
                    else:
                        logger.warning(f"Invalid configs format, starting fresh")
                        return self._get_default_configs()
            else:
                logger.info(f"Config file not found, creating with defaults")
                default_configs = self._get_default_configs()
                self._save_configs(default_configs)
                return default_configs
        except Exception as e:
            logger.error(f"Error loading configs: {e}")
            return self._get_default_configs()
    
    def _get_default_configs(self) -> List[Dict]:
        """Get default newsletter configuration"""
        default_config = {
            "id": "default_ai_newsletter",
            "name": "AI Daily Newsletter",
            "description": "Daily AI and technology news digest",
            "enabled": True,
            "feed_ids": [],  # Empty means use all enabled feeds
            "category_ids": [],  # Empty means use all enabled categories
            "max_stories": 12,
            "schedule_time": "07:00",
            "schedule_enabled": True,
            "sendfox_list_id": None,
            "branding": {
                "logo_enabled": True,
                "logo_path": "attached_assets/Innopower Logo white background_1760182832027.png",
                "header_color": "#000000",
                "header_text_color": "#cda600",
                "header_font": "Arial, sans-serif"
            },
            "cta_buttons": [
                {"text": "Visit Our Website", "link": "https://example.com"},
                {"text": "Subscribe for More", "link": "https://example.com/subscribe"},
                {"text": "Contact Us", "link": "https://example.com/contact"}
            ],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return [default_config]
    
    def _save_configs(self, configs: List[Dict] = None):
        """Save configurations to JSON file"""
        try:
            # Create backup before saving
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.backup"
                with open(self.config_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            
            # Save current data
            data_to_save = configs if configs is not None else self.configs
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Newsletter configs saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving configs: {e}")
    
    def get_all_configs(self) -> List[Dict]:
        """Get all newsletter configurations"""
        return self.configs
    
    def get_enabled_configs(self) -> List[Dict]:
        """Get only enabled newsletter configurations"""
        return [config for config in self.configs if config.get('enabled', True)]
    
    def get_config_by_id(self, config_id: str) -> Optional[Dict]:
        """Get configuration by ID"""
        for config in self.configs:
            if config.get('id') == config_id:
                return config
        return None
    
    def get_config_by_name(self, name: str) -> Optional[Dict]:
        """Get configuration by name"""
        for config in self.configs:
            if config.get('name', '').lower() == name.lower():
                return config
        return None
    
    def add_config(self, name: str, description: str = "", feed_ids: List[str] = None, 
                   category_ids: List[str] = None, max_stories: int = 12) -> bool:
        """Add a new newsletter configuration"""
        try:
            # Check if config with this name already exists
            if self.get_config_by_name(name):
                logger.warning(f"Newsletter config {name} already exists")
                return False
            
            # Generate ID from name
            config_id = name.lower().replace(' ', '_').replace('-', '_')
            
            new_config = {
                'id': config_id,
                'name': name,
                'description': description,
                'enabled': True,
                'feed_ids': feed_ids or [],
                'category_ids': category_ids or [],
                'max_stories': max_stories,
                'schedule_time': '07:00',
                'schedule_enabled': False,
                'sendfox_list_id': None,
                'branding': {
                    'logo_enabled': True,
                    'logo_path': 'attached_assets/Innopower Logo white background_1760182832027.png',
                    'header_color': '#000000',
                    'header_text_color': '#cda600',
                    'header_font': 'Arial, sans-serif'
                },
                'cta_buttons': [
                    {'text': 'Visit Our Website', 'link': 'https://example.com'},
                    {'text': 'Subscribe for More', 'link': 'https://example.com/subscribe'},
                    {'text': 'Contact Us', 'link': 'https://example.com/contact'}
                ],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            self.configs.append(new_config)
            self._save_configs()
            logger.info(f"Added newsletter config: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding config: {e}")
            return False
    
    def update_config(self, config_id: str, **kwargs) -> bool:
        """Update an existing newsletter configuration"""
        try:
            config = self.get_config_by_id(config_id)
            if not config:
                logger.warning(f"Config {config_id} not found")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if key in ['name', 'description', 'enabled', 'feed_ids', 'category_ids', 
                          'max_stories', 'schedule_time', 'schedule_enabled', 'sendfox_list_id', 'branding', 'cta_buttons']:
                    config[key] = value
            
            config['updated_at'] = datetime.now().isoformat()
            self._save_configs()
            logger.info(f"Updated newsletter config: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return False
    
    def delete_config(self, config_id: str) -> bool:
        """Delete a newsletter configuration"""
        try:
            # Don't allow deletion of default config if it's the only one
            if config_id == 'default_ai_newsletter' and len(self.configs) == 1:
                logger.warning("Cannot delete the only newsletter config")
                return False
            
            original_count = len(self.configs)
            self.configs = [c for c in self.configs if c.get('id') != config_id]
            
            if len(self.configs) < original_count:
                self._save_configs()
                logger.info(f"Deleted newsletter config: {config_id}")
                return True
            else:
                logger.warning(f"Config {config_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting config: {e}")
            return False
    
    def toggle_config(self, config_id: str) -> bool:
        """Toggle newsletter configuration enabled/disabled"""
        try:
            config = self.get_config_by_id(config_id)
            if not config:
                logger.warning(f"Config {config_id} not found")
                return False
            
            config['enabled'] = not config.get('enabled', True)
            config['updated_at'] = datetime.now().isoformat()
            self._save_configs()
            logger.info(f"Toggled config {config_id}: enabled={config['enabled']}")
            return True
            
        except Exception as e:
            logger.error(f"Error toggling config: {e}")
            return False
    
    def get_config_feeds(self, config_id: str, all_feeds: List[Dict]) -> List[Dict]:
        """Get RSS feeds for a specific newsletter configuration"""
        config = self.get_config_by_id(config_id)
        if not config:
            return all_feeds
        
        feed_ids = config.get('feed_ids', [])
        
        # Empty list means use all enabled feeds
        if not feed_ids:
            return [f for f in all_feeds if f.get('enabled', True)]
        
        # Filter to specified feeds that are also enabled
        return [f for f in all_feeds if f.get('id') in feed_ids and f.get('enabled', True)]
    
    def get_config_categories(self, config_id: str, all_categories: List[Dict]) -> List[str]:
        """Get category names for a specific newsletter configuration"""
        config = self.get_config_by_id(config_id)
        if not config:
            return [cat['name'] for cat in all_categories if cat.get('enabled', True)]
        
        category_ids = config.get('category_ids', [])
        
        # Empty list means use all enabled categories
        if not category_ids:
            return [cat['name'] for cat in all_categories if cat.get('enabled', True)]
        
        # Filter to specified categories that are also enabled
        return [cat['name'] for cat in all_categories 
                if cat.get('id') in category_ids and cat.get('enabled', True)]
