from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, conint
from datetime import datetime
from typing import Literal, Optional

#creazione dell'utente
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int 
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

#token per l'autenticazione
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None 

#creazione wallet
class WalletCreate(BaseModel):
    valuta: str

class WalletResponse(BaseModel):
    id: int
    owner_id: int
    valuta: str
    balance: float
    created_at: datetime

    class Config:
        orm_mode = True

#PER I DEPOSITI E PRELIEVO
class WalletDeposit(BaseModel):
    deposit: Decimal

class WalletWithdraw(BaseModel):
    withdraw: Decimal

#creazione transazione
class TransacionCreate(BaseModel):
    type: Literal["BUY", "SELL", "DEPOSIT", "WITHDRAW"]
    asset: str
    quantità: Decimal

class TransacionResponse(BaseModel):
    id: int
    wallet_id: int

    type: str #buy o sell
    asset: str
    quantità: Decimal
    price: Decimal
    status: str
    created_at: datetime

    class Config:
        from_attributes = True