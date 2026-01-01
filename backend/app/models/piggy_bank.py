from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class PiggyBank(Base):
    __tablename__ = "piggy_banks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    name = Column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint("account_id", "name", name="uq_account_piggy_bank"),
    )

    account = relationship("Account", back_populates="piggy_banks")
