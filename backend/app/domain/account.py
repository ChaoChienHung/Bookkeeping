# domain/accounts.py
from models.account import Account
from db.repositories.account_repo import AccountRepository

def create_account(name: str, repo: AccountRepository):
    # business validation
    if len(name) < 3:
        raise ValueError("Account name too short")
    return repo.create(name=name)

def get_accounts(repo: AccountRepository):
    return repo.list_all()
