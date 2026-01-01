import re
from app.db.repositories.piggy_bank_repo import PiggyBankRepository

NAME_PATTERN = re.compile(r"^[\w\-]+$")

def create_piggy_bank(
    user_id: int,
    account_id: int,
    name: str,
    repo: PiggyBankRepository,
):
    if not NAME_PATTERN.match(name):
        raise ValueError(
            "Invalid piggy bank name. Use alphanumeric, hyphen, underscore."
        )

    existing = repo.get_by_name(account_id, name)
    if existing:
        raise ValueError("Piggy bank already exists in this account")

    return repo.create(user_id, account_id, name)


def list_piggy_banks(
    user_id: int,
    account_id: int,
    repo: PiggyBankRepository,
):
    return repo.list_by_account(user_id, account_id)
