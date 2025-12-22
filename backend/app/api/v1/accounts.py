"""
API Routes - Account Management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.core.accounts import AccountManager

router = APIRouter()
account_manager = AccountManager()


class AccountCreate(BaseModel):
    name: str


class AccountResponse(BaseModel):
    name: str
    path: str
    exists: bool


@router.get("/accounts", response_model=List[AccountResponse])
async def list_accounts():
    """
    List all accounts
    """
    accounts = account_manager.list_accounts()
    return accounts


@router.post("/accounts", status_code=201)
async def create_account(account: AccountCreate):
    """
    Create a new account
    """
    result = account_manager.create_account(account.name)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/accounts/{account_name}")
async def get_account(account_name: str):
    """
    Get account details
    """
    account = account_manager.get_account(account_name)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account


@router.delete("/accounts/{account_name}")
async def delete_account(account_name: str, delete_data: bool = False):
    """
    Delete an account
    """
    result = account_manager.delete_account(account_name, delete_data)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result
