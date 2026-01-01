import os
import json
from typing import List
from backend.app.config.config import settings


class CategoryManager:
    """
    Manages transaction categories
    """
    
    def __init__(self, categories_file: str = None):
        self.categories_file = categories_file or os.path.join(
            settings.DATA_BASE_DIR,
            "categories.json"
        )
        os.makedirs(os.path.dirname(self.categories_file), exist_ok=True)
    
    def load_categories(self) -> List[str]:
        """Load categories from file"""
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    cats = json.load(f)
                    if not isinstance(cats, list):
                        cats = []
            except (json.JSONDecodeError, IOError):
                cats = []
        else:
            cats = []
        
        # Use defaults if empty
        if not cats:
            cats = settings.DEFAULT_CATEGORIES.copy()
            self.save_categories(cats)
        
        cats.sort()
        return cats
    
    def save_categories(self, categories: List[str]) -> None:
        """Save categories to file"""
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)
    
    def add_category(self, category: str) -> dict:
        """Add a new category"""
        category = category.strip()
        
        if not category:
            return {
                "success": False,
                "error": "Category name cannot be empty."
            }
        
        categories = self.load_categories()
        
        if category in categories:
            return {
                "success": False,
                "error": f"Category '{category}' already exists."
            }
        
        categories.append(category)
        categories.sort()
        self.save_categories(categories)
        
        return {
            "success": True,
            "category": category,
            "message": f"Category '{category}' added successfully."
        }
    
    def delete_category(self, category: str) -> dict:
        """Delete a category"""
        categories = self.load_categories()
        
        if category not in categories:
            return {
                "success": False,
                "error": f"Category '{category}' not found."
            }
        
        categories.remove(category)
        self.save_categories(categories)
        
        return {
            "success": True,
            "message": f"Category '{category}' deleted successfully."
        }
    
    def update_category(self, old_name: str, new_name: str) -> dict:
        """Update/rename a category"""
        new_name = new_name.strip()
        
        if not new_name:
            return {
                "success": False,
                "error": "New category name cannot be empty."
            }
        
        categories = self.load_categories()
        
        if old_name not in categories:
            return {
                "success": False,
                "error": f"Category '{old_name}' not found."
            }
        
        if new_name in categories and new_name != old_name:
            return {
                "success": False,
                "error": f"Category '{new_name}' already exists."
            }
        
        categories[categories.index(old_name)] = new_name
        categories.sort()
        self.save_categories(categories)
        
        return {
            "success": True,
            "old_name": old_name,
            "new_name": new_name,
            "message": f"Category renamed from '{old_name}' to '{new_name}'."
        }
    
    def get_categories(self) -> List[str]:
        """Get all categories"""
        return self.load_categories()
