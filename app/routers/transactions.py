from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import desc
from app import oauth2
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List

router = APIRouter(
    tags=['Transactions']
)

@router.post("/deposit", status_code=status.HTTP_200_OK, response_model=schemas.WalletResponse)
def deposito(deposito: schemas.WalletDeposit, db: Session = Depends(get_db),
              current_user: models.User = Depends(oauth2.get_current_user)):
    
    wallet = db.query(models.Wallet).filter(models.Wallet.owner_id == current_user.id).first()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet non trovato")
    
    if deposito.deposit > 0:
       wallet.balance += deposito.deposit
    else:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                           detail="L'importo è inferiore di zero")
    
    #CREIAMO ANCHE LA TRANSAZIONE QUANDO SI FA IL DEPOSITO
    transaction = models.Transaction(
        wallet_id = wallet.id,
        asset = wallet.valuta,
        type = "DEPOSIT",
        quantità = deposito.deposit,
        price = "1",
        status = "COMPLETED"
    )
    db.add(transaction)
    db.commit()
    db.refresh(wallet)
    return wallet

@router.post("/withdraw", status_code=status.HTTP_200_OK, response_model=schemas.WalletResponse)
def prelievo(prelievo: schemas.WalletWithdraw, db: Session = Depends(get_db),
              current_user: models.User = Depends(oauth2.get_current_user)):
   
    wallet = db.query(models.Wallet).filter(models.Wallet.owner_id == current_user.id).first()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet non trovato")
   
    if prelievo.withdraw > 0:
        
        if prelievo.withdraw > wallet.balance:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                           detail="Stai cercando di prelevare più di quanto hai sul conto")
        else: wallet.balance -= prelievo.withdraw
    else:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                           detail="L'importo è inferiore di zero")
    
    #CREIAMO ANCHE LA TRANSAZIONE QUANDO SI FA IL PRELEIVO
    transaction = models.Transaction(
        wallet_id = wallet.id,
        asset = wallet.valuta,
        type = "WITHDRAW",
        quantità = prelievo.withdraw,
        price = "1",
        status = "COMPLETED"
    )
    db.add(transaction)
    db.commit()
    db.refresh(wallet)
    return wallet

@router.post("/transaction", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.TransacionResponse)
def buy(transazione: schemas.TransacionCreate, db: Session = Depends(get_db),
         current_user: models.User = Depends(oauth2.get_current_user)):
    asset = transazione.asset
    price = utils.get_real_price(asset)

    totale_pagato_o_venduto = transazione.quantità * price

    #cerco nel database il suo conto e gli aggiungo la transazione
    wallet = db.query(models.Wallet).filter(models.Wallet.owner_id == current_user.id).first()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet non trovato")
    
    if transazione.type == "BUY":
       if totale_pagato_o_venduto > wallet.balance:
           raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                               detail="non hai una cifra sufficiente nel conto")
       else:
            wallet.balance -= totale_pagato_o_venduto

    elif transazione.type == "SELL":
      wallet.balance += totale_pagato_o_venduto

    new_transaction = models.Transaction(
       wallet_id=wallet.id,
       price=price,
       status="COMPLETED",
       **transazione.model_dump())
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


#per vedere le transazioni di account+
@router.get("/transaction", response_model=List[schemas.TransacionResponse])
def get_transactions(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    wallet = db.query(models.Wallet).filter(models.Wallet.owner_id == current_user.id).first()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="non hai un wallet")
    transazioni = db.query(models.Transaction).filter(models.Transaction.wallet_id == wallet.id).order_by(
        desc(models.Transaction.created_at)).all()
    return transazioni