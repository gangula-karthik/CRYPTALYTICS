from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import yfinance as yf
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from functools import lru_cache

nltk.download('vader_lexicon')



app = Flask(__name__)
sia = SentimentIntensityAnalyzer()


@lru_cache(maxsize=1)
def get_price():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url).json()
    return response

def top3crypto(data):
    data_sorted = sorted(data, key=lambda x: float(x['priceChangePercent']), reverse=True)
    top_3 = data_sorted[0:3]
    return top_3

@app.route('/pricechange', methods=['GET'])
def dayPriceChange(): 
    data = get_price()
    topcrypto = top3crypto(data)
    return render_template('pricechange.html', data=data, top=topcrypto)


def get_news(search_query):
    url = f"https://newsapi.org/v2/everything?q={search_query}&language=en&sortBy=publishedAt&apiKey=1b79f31f4909475bbfeadd33d9e08df3"
    response = requests.get(url)
    data = response.json()["articles"]
    x = 0
    news = []
    for i in range(len(data)):
        if search_query:
            if search_query.lower() in data[i]["title"].lower():
                news.append(data[i])
                x += 1
    return news


def NewsHeadlines(obj): 
    lst = []
    for i in obj: 
        lst.append(i['title'])
    return lst

def AverageSentimentOverall(res):
    pos, neg = [], []
    for scores in res:
        pos.append(scores['pos'])
        neg.append(scores['neg'])
    avg_pos = sum(pos) / len(pos) if pos else 0
    avg_neg = sum(neg) / len(neg) if neg else 0
    return {"pos": round(avg_pos * 100, 5), "neg": round(avg_neg * 100, 5)}


def analyze_sentiment(headline):
    sentiment_score = sia.polarity_scores(headline)
    return sentiment_score

@app.route('/cryptonews', methods=['GET'])
def news():
    search_query = request.args.get('search')
    news_data = get_news(search_query)
    headlines = NewsHeadlines(news_data)
    sentiment = [analyze_sentiment(i) for i in headlines]
    sentimentscore = AverageSentimentOverall(sentiment)
    return render_template('news.html', news=news_data, sentiment=sentimentscore)

def get_data(ticker):
    ticker = yf.Ticker(ticker)
    data = ticker.history(period="max")
    return data

@app.route('/crypto/<ticker>')
def crypto_data(ticker):
    return render_template('crypto_chart.html', ticker=ticker)

@app.route('/crypto-data/<ticker>')
def crypto_data_json(ticker):
    data = get_data(ticker)
    data_json = data.reset_index().to_json(orient='records', date_format='iso')
    return Response(data_json, content_type='application/json')

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


# lsof -nti:5000 | xargs kill -9