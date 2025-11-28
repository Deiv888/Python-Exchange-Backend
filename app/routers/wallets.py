from fastapi import Response, status, HTTPException, Depends, APIRouter
from app import oauth2
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List

router = APIRouter(
    tags=['Wallets']
)

@router.post("/wallet", status_code=status.HTTP_201_CREATED, response_model=schemas.WalletResponse)
def create_wallet(wallet: schemas.WalletCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(oauth2.get_current_user)):
    
    number = db.query(models.Wallet).filter(models.Wallet.owner_id == current_user.id).count()
    if number >=1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"l'utente {current_user.id} ha gia il numero masismo di account")
    
    if wallet.valuta not in ["EUR", "USD"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Stai selezionando una valuta non valida, scegli tra EUR o USD")

    new_wallet = models.Wallet(owner_id=current_user.id, **wallet.model_dump())
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return new_wallet

@router.get("/wallet", response_model=List[schemas.WalletResponse])
def get_wallet(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    id_user = current_user.id
    results = db.query(models.Wallet).filter(models.Wallet.owner_id == id_user).all()

    return results

#ELIMINARE UN WALLET
@router.delete("/wallet/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wallet(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    wallet = db.query(models.Wallet).filter(models.Wallet.id == id)
    wallet_delete = wallet.first()

    if not wallet_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Il wallet con id {id} non è stato trovato o non esiste")
    
    if wallet_delete.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Il wallet che stai cercando di eliminare non è tuo")
    
    #POI AGGIUNGO LA LOGICA CHE SE HA SALDO NON POSSO ELIMINARLO
    
    wallet.delete(synchronize_session=False)
    db.commit() 
    return Response(status_code=status.HTTP_204_NO_CONTENT)