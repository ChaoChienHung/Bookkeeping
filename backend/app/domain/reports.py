"""
Core Business Logic - Report Generation
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List
from app.core.transactions import TransactionManager


class ReportGenerator:
    """
    Generates financial reports and analytics
    """
    
    def __init__(self, transaction_manager: TransactionManager):
        self.tm = transaction_manager
    
    def generate_monthly_report(self, year: int, month: int) -> Dict:
        """
        Generate monthly financial report
        """
        start = datetime(year, month, 1)
        end = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
        
        # Filter transactions for the month
        month_df = self.tm.transactions_df[
            (self.tm.transactions_df['Date'] >= start) &
            (self.tm.transactions_df['Date'] < end)
        ]
        
        # Calculate balance before month
        balance_before = self.tm.transactions_df[
            self.tm.transactions_df['Date'] < start
        ]['Amount'].sum()
        
        # Calculate income and expenses
        income = month_df[month_df['Amount'] > 0]['Amount'].sum()
        expenses = month_df[month_df['Amount'] < 0]['Amount'].sum()
        net = income + expenses
        balance_after = balance_before + net
        
        # Expense breakdown by category
        expense_by_category = {}
        if not month_df.empty:
            expense_df = month_df[
                (month_df['Amount'] < 0) &
                (month_df['Category'].str.lower() != 'savings')
            ]
            if not expense_df.empty:
                expense_by_category = (
                    expense_df.groupby('Category')['Amount']
                    .sum()
                    .sort_values()
                    .to_dict()
                )
        
        # Income breakdown by category
        income_by_category = {}
        if not month_df.empty:
            income_df = month_df[month_df['Amount'] > 0]
            if not income_df.empty:
                income_by_category = (
                    income_df.groupby('Category')['Amount']
                    .sum()
                    .sort_values(ascending=False)
                    .to_dict()
                )
        
        return {
            "year": year,
            "month": month,
            "period": f"{year}-{month:02d}",
            "balance_before": float(balance_before),
            "income": float(income),
            "expenses": float(expenses),
            "net": float(net),
            "balance_after": float(balance_after),
            "transaction_count": len(month_df),
            "expense_by_category": {k: float(v) for k, v in expense_by_category.items()},
            "income_by_category": {k: float(v) for k, v in income_by_category.items()}
        }
    
    def generate_yearly_report(self, year: int) -> Dict:
        """Generate yearly financial report"""
        start = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        
        # Filter transactions for the year
        year_df = self.tm.transactions_df[
            (self.tm.transactions_df['Date'] >= start) &
            (self.tm.transactions_df['Date'] < end)
        ]
        
        # Calculate balance before year
        balance_before = self.tm.transactions_df[
            self.tm.transactions_df['Date'] < start
        ]['Amount'].sum()
        
        # Calculate income and expenses
        income = year_df[year_df['Amount'] > 0]['Amount'].sum()
        expenses = year_df[year_df['Amount'] < 0]['Amount'].sum()
        net = income + expenses
        balance_after = balance_before + net
        
        # Expense breakdown by category
        expense_by_category = {}
        if not year_df.empty:
            expense_df = year_df[year_df['Amount'] < 0]
            if not expense_df.empty:
                expense_by_category = (
                    expense_df.groupby('Category')['Amount']
                    .sum()
                    .sort_values()
                    .to_dict()
                )
        
        # Income breakdown by category
        income_by_category = {}
        if not year_df.empty:
            income_df = year_df[year_df['Amount'] > 0]
            if not income_df.empty:
                income_by_category = (
                    income_df.groupby('Category')['Amount']
                    .sum()
                    .sort_values(ascending=False)
                    .to_dict()
                )
        
        # Monthly summary
        monthly_summary = []
        for month in range(1, 13):
            month_start = datetime(year, month, 1)
            month_end = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
            
            month_df = year_df[
                (year_df['Date'] >= month_start) &
                (year_df['Date'] < month_end)
            ]
            
            monthly_income = month_df[month_df['Amount'] > 0]['Amount'].sum()
            monthly_expenses = month_df[month_df['Amount'] < 0]['Amount'].sum()
            
            monthly_summary.append({
                "month": month,
                "income": float(monthly_income),
                "expenses": float(monthly_expenses),
                "net": float(monthly_income + monthly_expenses)
            })
        
        return {
            "year": year,
            "balance_before": float(balance_before),
            "income": float(income),
            "expenses": float(expenses),
            "net": float(net),
            "balance_after": float(balance_after),
            "transaction_count": len(year_df),
            "expense_by_category": {k: float(v) for k, v in expense_by_category.items()},
            "income_by_category": {k: float(v) for k, v in income_by_category.items()},
            "monthly_summary": monthly_summary
        }
    
    def get_category_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        Get spending summary by category for a date range
        """
        df = self.tm.transactions_df.copy()
        
        if start_date:
            df = df[df['Date'] >= pd.to_datetime(start_date)]
        
        if end_date:
            df = df[df['Date'] <= pd.to_datetime(end_date)]
        
        # Separate income and expenses
        expense_df = df[df['Amount'] < 0]
        income_df = df[df['Amount'] > 0]
        
        expense_by_category = (
            expense_df.groupby('Category')['Amount']
            .sum()
            .sort_values()
            .to_dict()
        )
        
        income_by_category = (
            income_df.groupby('Category')['Amount']
            .sum()
            .sort_values(ascending=False)
            .to_dict()
        )
        
        return {
            "total_income": float(income_df['Amount'].sum()),
            "total_expenses": float(expense_df['Amount'].sum()),
            "expense_by_category": {k: float(v) for k, v in expense_by_category.items()},
            "income_by_category": {k: float(v) for k, v in income_by_category.items()}
        }
