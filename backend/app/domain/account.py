import os
import json
import re
from backend.app.config import settings
from typing import List, Optional


class AccountManager:
    """
    Manages user accounts
    """
    
    def __init__(self, accounts_file: str = None):
        self.accounts_file = accounts_file or os.path.join(
            settings.DATA_BASE_DIR, 
            "accounts.json"
        )
        os.makedirs(os.path.dirname(self.accounts_file), exist_ok=True)
    
    def load_accounts(self) -> List[str]:
        """
        Load all accounts from file
        """
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_accounts(self, accounts: List[str]) -> None:
        """
        Save accounts to file
        """
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)
    
    def create_account(self, account_name: str) -> dict:
        """
        Create a new account
        """
        if not self.validate_account_name(account_name):
            return {
                "success": False,
                "error": "Invalid account name. Use only alphanumeric characters, hyphens, and underscores."
            }
        
        accounts = self.load_accounts()
        
        if account_name in accounts:
            return {
                "success": False,
                "error": f"Account '{account_name}' already exists."
            }
        
        accounts.append(account_name)
        self.save_accounts(accounts)
        
        # ------------------------
        # Create Account Directory
        # ------------------------
        account_dir = os.path.join(settings.USER_DATA_DIR, account_name)
        os.makedirs(account_dir, exist_ok=True)
        
        return {
            "success": True,
            "account_name": account_name,
            "message": f"Account '{account_name}' created successfully."
        }
    
    def get_account(self, account_name: str) -> Optional[dict]:
        """Get account details"""
        accounts = self.load_accounts()
        if account_name not in accounts:
            return None
        
        account_dir = os.path.join(settings.USER_DATA_DIR, account_name)
        return {
            "name": account_name,
            "path": account_dir,
            "exists": os.path.exists(account_dir)
        }
    
    def list_accounts(self) -> List[dict]:
        """List all accounts with details"""
        accounts = self.load_accounts()
        result = []
        
        for account in accounts:
            account_dir = os.path.join(settings.USER_DATA_DIR, account)
            result.append({
                "name": account,
                "path": account_dir,
                "exists": os.path.exists(account_dir)
            })
        
        return result
    
    def delete_account(self, account_name: str, delete_data: bool = False) -> dict:
        """Delete an account (optionally with data)"""
        accounts = self.load_accounts()
        
        if account_name not in accounts:
            return {
                "success": False,
                "error": f"Account '{account_name}' not found."
            }
        
        accounts.remove(account_name)
        self.save_accounts(accounts)
        
        if delete_data:
            import shutil
            account_dir = os.path.join(settings.USER_DATA_DIR, account_name)
            if os.path.exists(account_dir):
                shutil.rmtree(account_dir)
        
        return {
            "success": True,
            "message": f"Account '{account_name}' deleted successfully."
        }
    
    @staticmethod
    def validate_account_name(name: str) -> bool:
        """
        Validate account name format
        """
        return bool(re.match(r"^[\w\-]+$", name))