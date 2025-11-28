from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from datetime import datetime, timedelta
from . import schemas, models
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict):
    copia = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    copia.update({"exp": expire})

    token = jwt.encode(copia, SECRET_KEY, algorithm=ALGORITHM)

    return token

def verify_access_token(token: str, credentials_exceptions):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("user_id")
        if not id:
            raise credentials_exceptions
        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exceptions
    
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"credenziali non valide", headers={"WWW-Authenticate": "Bearer"})
    
    token = verify_access_token(token, credential_exceptions)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user