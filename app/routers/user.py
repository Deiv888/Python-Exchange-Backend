from fastapi import APIRouter, Response, status, HTTPException, Depends

from app import oauth2
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import get_db, engine
from typing import List

router = APIRouter(
    tags=['User']
)

#creazione dell'utente
@router.post("/user", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(nuovoUtente: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.hash(nuovoUtente.password)
    nuovoUtente.password = hashed_password

    new_user = models.User(**nuovoUtente.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

#restituzione utenti creati
@router.get("/user", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):

    users = db.query(models.User).all()
    return users

#aggiornare un utente (solo se loggato)
@router.put("/user/{id}", status_code=status.HTTP_202_ACCEPTED ,response_model=schemas.UserResponse)
def update_user(id: int, utenteAggiornato: schemas.UserCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):

    utente = db.query(models.User).filter(models.User.id == id)
    utente_da_aggiornare = utente.first()

    if not utente_da_aggiornare:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"utente con id = {id} non esiste")
    
    if utente_da_aggiornare.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Non sei autorizzato")
    
    hashed_password = utils.hash(utenteAggiornato.password)
    utenteAggiornato.password = hashed_password
    utente.update(utenteAggiornato.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(utente_da_aggiornare)
    return utente_da_aggiornare

#eliminare un utente (solo se loggato)
@router.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
     
    utente_da_eliminare = db.query(models.User).filter(models.User.id == id)
    
    if not utente_da_eliminare.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"utente con id = {id} non esiste")
    
    if utente_da_eliminare.first().id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Non sei autorizzato")
    
    utente_da_eliminare.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#restituzione dei dati del suo account all'utente (solo se loggato)
@router.get("/user/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def get_user_by_id(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    utente = db.query(models.User).filter(models.User.id == id).first()

    if not utente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"utente con id = {id} non esiste")
    
    if utente.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Non sei autorizzato")
    return utente