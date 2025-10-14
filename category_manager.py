import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CategoryManager:
    def __init__(self, categories_file: str = "categories.json"):
        self.categories_file = categories_file
        self.categories = self._load_categories()
    
    def _load_categories(self) -> List[Dict]:
        """Load categories from JSON file"""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    categories = json.load(f)
                    if isinstance(categories, list):
                        return categories
                    else:
                        logger.warning(f"Invalid categories format, starting fresh")
                        return self._get_default_categories()
            else:
                logger.info(f"Categories file not found, creating with defaults")
                default_categories = self._get_default_categories()
                self._save_categories(default_categories)
                return default_categories
        except Exception as e:
            logger.error(f"Error loading categories: {e}")
            return self._get_default_categories()
    
    def _get_default_categories(self) -> List[Dict]:
        """Get default categories"""
        default_cats = [
            {"id": "ai_policy", "name": "AI Policy", "emoji": "⚖️", "priority": 1, "enabled": True},
            {"id": "ai_business", "name": "AI Business", "emoji": "💼", "priority": 2, "enabled": True},
            {"id": "ai_research", "name": "AI Research", "emoji": "🔬", "priority": 3, "enabled": True},
            {"id": "ai_products", "name": "AI Products", "emoji": "🚀", "priority": 4, "enabled": True},
            {"id": "machine_learning", "name": "Machine Learning", "emoji": "🤖", "priority": 5, "enabled": True},
            {"id": "robotics", "name": "Robotics", "emoji": "🦾", "priority": 6, "enabled": True},
            {"id": "tech_industry", "name": "Tech Industry", "emoji": "💻", "priority": 7, "enabled": True},
            {"id": "other", "name": "Other", "emoji": "📰", "priority": 999, "enabled": True}
        ]
        
        for cat in default_cats:
            cat['added_at'] = datetime.now().isoformat()
        
        return default_cats
    
    def _save_categories(self, categories: List[Dict] = None):
        """Save categories to JSON file"""
        try:
            # Create backup before saving
            if os.path.exists(self.categories_file):
                backup_file = f"{self.categories_file}.backup"
                with open(self.categories_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            
            # Save current data
            data_to_save = categories if categories is not None else self.categories
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Categories saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving categories: {e}")
    
    def get_all_categories(self) -> List[Dict]:
        """Get all categories sorted by priority"""
        return sorted(self.categories, key=lambda x: x.get('priority', 999))
    
    def get_enabled_categories(self) -> List[Dict]:
        """Get only enabled categories"""
        return [cat for cat in self.get_all_categories() if cat.get('enabled', True)]
    
    def get_category_names(self, enabled_only: bool = True) -> List[str]:
        """Get list of category names"""
        categories = self.get_enabled_categories() if enabled_only else self.get_all_categories()
        return [cat['name'] for cat in categories]
    
    def get_category_by_id(self, category_id: str) -> Optional[Dict]:
        """Get category by ID"""
        for cat in self.categories:
            if cat.get('id') == category_id:
                return cat
        return None
    
    def get_category_by_name(self, name: str) -> Optional[Dict]:
        """Get category by name"""
        for cat in self.categories:
            if cat.get('name', '').lower() == name.lower():
                return cat
        return None
    
    def add_category(self, name: str, emoji: str = "📁", priority: int = None) -> bool:
        """Add a new category"""
        try:
            # Check if category already exists
            if self.get_category_by_name(name):
                logger.warning(f"Category {name} already exists")
                return False
            
            # Generate ID from name
            category_id = name.lower().replace(' ', '_').replace('-', '_')
            
            # Auto-assign priority if not provided (max 998 to keep "Other" at 999)
            if priority is None:
                # Exclude "Other" category when calculating max priority
                non_other_categories = [cat for cat in self.categories if cat.get('id') != 'other']
                max_priority = max([cat.get('priority', 0) for cat in non_other_categories], default=0)
                priority = min(max_priority + 1, 998)
            
            new_category = {
                'id': category_id,
                'name': name,
                'emoji': emoji,
                'priority': priority,
                'enabled': True,
                'added_at': datetime.now().isoformat()
            }
            
            self.categories.append(new_category)
            self._save_categories()
            logger.info(f"Added category: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding category: {e}")
            return False
    
    def update_category(self, category_id: str, name: str = None, emoji: str = None, 
                       priority: int = None) -> bool:
        """Update an existing category"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                logger.warning(f"Category {category_id} not found")
                return False
            
            if name is not None:
                category['name'] = name
            if emoji is not None:
                category['emoji'] = emoji
            if priority is not None:
                category['priority'] = priority
            
            category['updated_at'] = datetime.now().isoformat()
            self._save_categories()
            logger.info(f"Updated category: {category_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating category: {e}")
            return False
    
    def delete_category(self, category_id: str) -> bool:
        """Delete a category"""
        try:
            # Don't allow deletion of "Other" category
            if category_id == 'other':
                logger.warning("Cannot delete 'Other' category")
                return False
            
            original_count = len(self.categories)
            self.categories = [cat for cat in self.categories if cat.get('id') != category_id]
            
            if len(self.categories) < original_count:
                self._save_categories()
                logger.info(f"Deleted category: {category_id}")
                return True
            else:
                logger.warning(f"Category {category_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return False
    
    def toggle_category(self, category_id: str) -> bool:
        """Toggle category enabled/disabled"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                logger.warning(f"Category {category_id} not found")
                return False
            
            category['enabled'] = not category.get('enabled', True)
            self._save_categories()
            logger.info(f"Toggled category {category_id}: enabled={category['enabled']}")
            return True
            
        except Exception as e:
            logger.error(f"Error toggling category: {e}")
            return False
    
    def reorder_categories(self, category_id: str, new_priority: int) -> bool:
        """Change the priority/order of a category"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                logger.warning(f"Category {category_id} not found")
                return False
            
            category['priority'] = new_priority
            self._save_categories()
            logger.info(f"Reordered category {category_id} to priority {new_priority}")
            return True
            
        except Exception as e:
            logger.error(f"Error reordering category: {e}")
            return False
