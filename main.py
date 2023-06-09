from flask import Flask, render_template, request, jsonify, Response, session
import requests
import json
import yfinance as yf
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from functools import lru_cache
from getpass import getpass
from langchain.llms import AI21
from langchain import PromptTemplate, LLMChain
from flask_session import Session


nltk.download('vader_lexicon')



app = Flask(__name__)
sia = SentimentIntensityAnalyzer()


@lru_cache(maxsize=1)
def get_price():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url).json()
    print(response)
    return response

def top3crypto(data):
    # data_sorted = sorted(data, key=lambda x: float(x['priceChangePercent']), reverse=True)
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
    print("hello world")
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

# @app.route('/api_key', methods=['POST'])
# def api_key():
#     key = request.json.get('key', None)
#     if key:
#         result = maingpt(None, key)  
#         return jsonify(result), 200
#     else:
#         return jsonify({'message': 'No key provided'}), 400



# @app.route('/cryptogpt', methods=['GET', 'POST'])
# def gptcrypto():
#     if request.method == 'POST':
#         text_input = request.form.get('messageInput')
#         answer = maingpt(text_input)
#         return jsonify({'answer': answer})
#     else:
#         return render_template('cryptogpt.html') 

app.config['SECRET_KEY'] = 'cryptalytics123'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/api_key', methods=['POST'])
def api_key():
    key = request.form.get('apiKey', None)
    if key:
        session['api_key'] = key
        return jsonify({'message': 'Success'}), 200
    else:
        return jsonify({'message': 'No key provided'}), 400
    
def maingpt(msg, AI21_API_KEY):
    template = """Question: {question}

    Answer: Let's think step by step."""
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm = AI21(ai21_api_key=AI21_API_KEY)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    question = msg
    ans = llm_chain.run(question)
    return ans 

@app.route('/cryptogpt', methods=['GET', 'POST'])
def gptcrypto():
    if request.method == 'POST':
        text_input = request.form.get('messageInput')
        api_key = session.get('api_key', None)
        if not api_key:
            return jsonify({'message': 'No API key in session'}), 400
        answer = maingpt(text_input, api_key)
        return jsonify({'answer': answer})
    else:
        return render_template('cryptogpt.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


# lsof -nti:5000 | xargs kill -9