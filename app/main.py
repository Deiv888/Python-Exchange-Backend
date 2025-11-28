from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.routers import auth, transactions, user, wallets
from .database import engine

#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]#domini che possono fare richieste al mio backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#routers
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(wallets.router)
app.include_router(transactions.router)

#home
@app.get("/")
def home():
    return{"message": "Benvenuto nell'Exchange di Davide"}