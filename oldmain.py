from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from yahooquery import Screener
import requests
import keyring
import json

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/crypto/{ticker}")
async def get_data(ticker):
    ticker = yf.Ticker(ticker)
    data = ticker.history(period="max")
    data = data.to_json()
    return json.dumps(data, indent=4)


@app.get("/list")
def getTickers():
    s = Screener()
    data = s.get_screeners('all_cryptocurrencies_us', count=250)
    dicts = data['all_cryptocurrencies_us']['quotes']
    symbols = [d['symbol'] for d in dicts]
    return  {"response": symbols}


@app.get("/realtime")
async def getRealTimePrice4All():
    try:
        r = requests.get("https://www.okx.com/api/v5/market/tickers?instType=SPOT")
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    else:
        data = r.json()
        return data
    

@app.get("/realtime/{ticker}")
async def getRealTimePrice(ticker):
    try:
        r = requests.get(f"https://www.okx.com/api/v5/market/ticker?instId={ticker}-SWAP")
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    else:
        data = r.json()
        return data
    
@app.get("/daypricechange")
async def dayPriceChange(): 
    '''
    Returns the 24 hour price change for all the cryptocurrencies
    '''
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url).json()
    return response

def apiKeyRetrieve(name, username):
    return keyring.get_password(name, username)

@app.get("/news")
async def latestNews():
    API_KEY = apiKeyRetrieve("cryptoNewsApi", "karthik")
    url = f"https://newsapi.org/v2/everything?q=bitcoin&apiKey={str(API_KEY)}"
    response = requests.get(url).json()
    return response