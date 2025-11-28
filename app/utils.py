from passlib.context import CryptContext
import yfinance as yf
from decimal import Decimal, InvalidOperation

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(password_inserita, hashed_password):
    return pwd_context.verify(password_inserita, hashed_password)

def get_real_price(ticker: str) -> Decimal:
    
    ticker = ticker.upper().strip()

    crypto_mapping = ["BTC", "ETH", "SOL", "DOGE", "XRP", "ADA"]
    
    if ticker in crypto_mapping:
        yahoo_ticker = f"{ticker}-USD"
    else:
        yahoo_ticker = ticker

    try:
        data = yf.download(tickers=yahoo_ticker, period="1d", interval="1m", progress=False, auto_adjust=True)

        if data.empty:
            print(f"Errore: Nessun dato trovato per {ticker}")
            return None

        last_price = data['Close'].iloc[-1].item()
        
        return Decimal(f"{last_price}")

    except Exception as e:
        print(f"Errore durante il recupero del prezzo per {ticker}: {e}")
        return None