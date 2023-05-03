from flask import Flask, render_template
import requests
import json


app = Flask(__name__)

def get_news():
    url = "https://newsapi.org/v2/everything?q=btc-usd&language=en&sortBy=publishedAt&apiKey=1b79f31f4909475bbfeadd33d9e08df3"
    response = requests.get(url)
    data = response.json()["articles"]
    x = 0
    news = []
    for i in range(len(data)):
        if "bitcoin" in data[i]["title"].lower():
            news.append(data[i])
            x += 1
    return news

@app.route('/')
def index():
    news_data = get_news()
    return render_template('news.html', news=news_data) 

if __name__ == '__main__':
    app.run(debug=True)


# lsof -nti:5000 | xargs kill -9