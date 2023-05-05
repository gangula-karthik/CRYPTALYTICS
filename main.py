from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import yfinance as yf


app = Flask(__name__)



def get_price():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url).json()
    return response

@app.route('/pricechange', methods=['GET'])
def dayPriceChange(): 
    response = get_price()
    topcrypto = top3crypto()
    return render_template('pricechange.html', data=response, top=topcrypto)

def top3crypto():
    url = 'https://api1.binance.com/api/v3/ticker/24hr'
    response = requests.get(url)
    data = response.json()
    data_sorted = sorted(data, key=lambda x: x['priceChangePercent'], reverse=True)
    top_3 = data_sorted[0:3]
    return top_3


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

@app.route('/cryptonews', methods=['GET'])
def news():
    search_query = request.args.get('search')
    news_data = get_news(search_query)
    return render_template('news.html', news=news_data) 

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

if __name__ == '__main__':
    app.run(debug=True)


# lsof -nti:5000 | xargs kill -9