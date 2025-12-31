from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.repositories.piggy_bank_repo import PiggyBankRepository
from app.domain.piggy_banks import create_piggy_bank, list_piggy_banks
from app.schemas.piggy_bank import PiggyBankCreate, PiggyBankRead

router = APIRouter()

@router.post(
    "/accounts/{account_id}/piggy-banks",
    response_model=PiggyBankRead,
)
def create(
    account_id: int,
    payload: PiggyBankCreate,
    db: Session = Depends(get_db),
    user_id: int = 1,  # placeholder (from auth later)
):
    repo = PiggyBankRepository(db)

    try:
        return create_piggy_bank(
            user_id=user_id,
            account_id=account_id,
            name=payload.name,
            repo=repo,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/accounts/{account_id}/piggy-banks",
    response_model=list[PiggyBankRead],
)
def list_all(
    account_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1,
):
    repo = PiggyBankRepository(db)
    return list_piggy_banks(user_id, account_id, repo)
