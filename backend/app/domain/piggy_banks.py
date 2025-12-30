"""
Core Business Logic - Piggy Bank Management
"""
import os
import re
from typing import List, Optional
from app.config import settings


class PiggyBankManager:
    """
    Manages piggy banks (sub-accounts) within accounts
    """
    
    def __init__(self, account_name: str):
        self.account_name = account_name
        self.base_dir = os.path.join(
            settings.USER_DATA_DIR,
            account_name,
            "piggy_banks"
        )
        os.makedirs(self.base_dir, exist_ok=True)
    
    def list_piggy_banks(self) -> List[str]:
        """
        List all piggy banks for the account
        """
        if not os.path.exists(self.base_dir):
            return []
        
        return [
            name for name in os.listdir(self.base_dir)
            if os.path.isdir(os.path.join(self.base_dir, name))
        ]
    
    def create_piggy_bank(self, name: str) -> dict:
        """
        Create a new piggy bank
        """
        if not self.validate_name(name):
            return {
                "success": False,
                "error": "Invalid piggy bank name. Use only alphanumeric characters, hyphens, and underscores."
            }
        
        piggy_bank_dir = os.path.join(self.base_dir, name)
        
        if os.path.exists(piggy_bank_dir):
            return {
                "success": False,
                "error": f"Piggy bank '{name}' already exists."
            }
        
        # ---------------------------------------------
        # Create directory structure for the piggy bank
        # ---------------------------------------------
        os.makedirs(piggy_bank_dir, exist_ok=True)
        os.makedirs(os.path.join(piggy_bank_dir, "csv"), exist_ok=True)
        os.makedirs(os.path.join(piggy_bank_dir, "json"), exist_ok=True)
        
        return {
            "success": True,
            "name": name,
            "path": piggy_bank_dir,
            "message": f"Piggy bank '{name}' created successfully."
        }
    
    def get_piggy_bank(self, name: str) -> Optional[dict]:
        """
        Get piggy bank details
        """
        piggy_bank_dir = os.path.join(self.base_dir, name)
        
        if not os.path.exists(piggy_bank_dir):
            return None
        
        return {
            "name": name,
            "path": piggy_bank_dir,
            "account": self.account_name,
            "csv_path": os.path.join(piggy_bank_dir, "csv"),
            "json_path": os.path.join(piggy_bank_dir, "json")
        }
    
    def delete_piggy_bank(self, name: str, delete_data: bool = False) -> dict:
        """
        Delete a piggy bank (optionally with data)
        """
        piggy_bank_dir = os.path.join(self.base_dir, name)
        
        if not os.path.exists(piggy_bank_dir):
            return {
                "success": False,
                "error": f"Piggy bank '{name}' not found."
            }
        
        if delete_data:
            import shutil
            shutil.rmtree(piggy_bank_dir)
            return {
                "success": True,
                "message": f"Piggy bank '{name}' and all data deleted successfully."
            }
        else:
            # Just mark as deleted or move to trash
            return {
                "success": True,
                "message": f"Piggy bank '{name}' removed (data preserved)."
            }
    
    def get_folder_path(self, piggy_bank_name: str, extension: str = 'csv') -> str:
        """
        Get the folder path for a specific file type
        """
        return os.path.join(self.base_dir, piggy_bank_name, extension)
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate piggy bank name format
        """
        return bool(re.match(r"^[\w\-]+$", name))
