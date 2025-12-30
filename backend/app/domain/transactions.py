"""
Core Business Logic - Transaction Management
"""
import os
import glob
import re
import pandas as pd
from typing import Dict
from datetime import datetime
from app.config import settings


class TransactionManager:
    """
    Manages financial transactions
    """
    
    COLUMNS = ['Transaction ID', 'Date', 'Amount', 'Category', 'Description', 'Balance']
    
    def __init__(self, account_name: str, piggy_bank_name: str):
        self.account_name = account_name
        self.piggy_bank_name = piggy_bank_name
        self.base_path = os.path.join(
            settings.USER_DATA_DIR,
            account_name,
            "piggy_banks",
            piggy_bank_name
        )
        self.transactions_df = pd.DataFrame(columns=self.COLUMNS)
        self.transaction_counter = 1
        self.current_balance = 0.0
        self.loaded_year = None
    
    def get_file_path(self, year: int = None, extension: str = 'csv') -> str:
        """
        Get file path for a specific year
        """
        if year is None:
            year = datetime.now().year
        
        folder = os.path.join(self.base_path, extension)
        os.makedirs(folder, exist_ok=True)
        
        filename = f"{year}_transactions.{extension}"
        return os.path.join(folder, filename)
    
    def list_transaction_files(self, extension: str = 'csv') -> Dict[int, str]:
        """
        List all transaction files and return year -> filepath mapping
        """
        folder = os.path.join(self.base_path, extension)
        pattern = os.path.join(folder, f"*_transactions.{extension}")
        files = glob.glob(pattern)
        
        year_map = {}
        for f in files:
            name = os.path.basename(f)
            m = re.match(r"(\d{4})_transactions\." + extension + "$", name)
            if m:
                year_map[int(m.group(1))] = f
        
        return year_map
    
    def load_from_csv(self, year: int = None) -> dict:
        """Load transactions from CSV file"""
        files = self.list_transaction_files('csv')
        
        if not files:
            return {
                "success": False,
                "error": "No CSV files available."
            }
        
        if year is None:
            year = max(files.keys())
        
        self.loaded_year = year
        filepath = self.get_file_path(year, 'csv')
        
        try:
            self.transactions_df = pd.read_csv(filepath, parse_dates=['Date'])
        except FileNotFoundError:
            self.transactions_df = pd.DataFrame(columns=self.COLUMNS)
            self.current_balance = 0.0
            return {
                "success": False,
                "error": f"File not found: {filepath}"
            }
        
        # Ensure Balance column exists
        if 'Balance' not in self.transactions_df.columns:
            self._recalculate_balance()
        
        self.transactions_df.sort_values(
            by=['Date', 'Transaction ID'],
            inplace=True,
            ignore_index=True
        )
        
        self.transaction_counter = (
            self.transactions_df['Transaction ID'].max() + 1
            if not self.transactions_df.empty else 1
        )
        
        self.current_balance = (
            self.transactions_df['Balance'].iloc[-1]
            if not self.transactions_df.empty else 0.0
        )
        
        return {
            "success": True,
            "year": year,
            "count": len(self.transactions_df),
            "balance": self.current_balance
        }
    
    def save_to_csv(self, year: int = None) -> dict:
        """Save transactions to CSV file"""
        self.transactions_df.sort_values(
            by=['Date', 'Transaction ID'],
            inplace=True,
            ignore_index=True
        )
        
        filepath = self.get_file_path(year, 'csv')
        self.transactions_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return {
            "success": True,
            "filepath": filepath,
            "count": len(self.transactions_df)
        }
    
    def add_transaction(
        self,
        date: str,
        amount: float,
        category: str,
        description: str = ""
    ) -> dict:
        """Add a new transaction"""
        try:
            date_obj = pd.to_datetime(date)
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid date format: {str(e)}"
            }
        
        balance = self.current_balance + amount
        
        new_transaction = {
            'Transaction ID': self.transaction_counter,
            'Date': date_obj,
            'Amount': amount,
            'Category': category,
            'Description': description,
            'Balance': balance
        }
        
        self.transactions_df.loc[len(self.transactions_df)] = new_transaction
        self.current_balance = balance
        self.transaction_counter += 1
        
        self._refresh_balance()
        
        return {
            "success": True,
            "transaction": new_transaction,
            "balance": self.current_balance
        }
    
    def get_transactions(
        self,
        start_date: str = None,
        end_date: str = None,
        category: str = None
    ) -> pd.DataFrame:
        """Get filtered transactions"""
        df = self.transactions_df.copy()
        
        if start_date:
            df = df[df['Date'] >= pd.to_datetime(start_date)]
        
        if end_date:
            df = df[df['Date'] <= pd.to_datetime(end_date)]
        
        if category:
            df = df[df['Category'] == category]
        
        return df
    
    def delete_transaction_by_id(self, transaction_id: int) -> dict:
        """Delete a transaction by its ID"""
        idx = self.transactions_df[
            self.transactions_df['Transaction ID'] == transaction_id
        ].index
        
        if len(idx) == 0:
            return {
                "success": False,
                "error": f"Transaction ID {transaction_id} not found."
            }
        
        removed = self.transactions_df.loc[idx[0]]
        self.transactions_df = self.transactions_df.drop(idx).reset_index(drop=True)
        
        # Reassign IDs and recalculate balances
        self.transactions_df['Transaction ID'] = range(1, len(self.transactions_df) + 1)
        self._recalculate_balance()
        
        self.transaction_counter = len(self.transactions_df) + 1
        self.current_balance = (
            self.transactions_df['Balance'].iloc[-1]
            if not self.transactions_df.empty else 0.0
        )
        
        return {
            "success": True,
            "deleted": removed.to_dict(),
            "balance": self.current_balance
        }
    
    def _refresh_balance(self) -> None:
        """Refresh balance for all transactions"""
        if self.transactions_df.empty:
            return
        
        self.transactions_df.sort_values(
            by=['Date', 'Transaction ID'],
            inplace=True,
            ignore_index=True
        )
        
        balance = 0
        balances = []
        for amount in self.transactions_df['Amount']:
            balance += amount
            balances.append(balance)
        
        self.transactions_df['Balance'] = balances
        self.transaction_counter = self.transactions_df['Transaction ID'].max() + 1
        self.current_balance = balances[-1] if balances else 0.0
    
    def _recalculate_balance(self) -> None:
        """Recalculate balance column"""
        balance = 0
        balances = []
        for amount in self.transactions_df['Amount']:
            balance += amount
            balances.append(balance)
        
        self.transactions_df['Balance'] = balances
