import requests
import json

url = "https://newsapi.org/v2/everything?q=btc-usd&language=en&sortBy=publishedAt&apiKey=1b79f31f4909475bbfeadd33d9e08df3"

response = requests.get(url)
data = response.json()["articles"]
x = 0
for i in range(len(data)):
    if "bitcoin" in data[i]["title"].lower():
        print(str(x), str(data[i]))
        x += 1
    else: 
        pass
