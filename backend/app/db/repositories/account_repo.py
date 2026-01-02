# db/repositories/account_repo.py
from sqlalchemy.orm import Session
from models.account import Account

class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str) -> Account:
        account = Account(name=name)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def list_all(self):
        return self.db.query(Account).all()
