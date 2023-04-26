import websocket
import json
import ssl
from datetime import datetime

class BinanceWebSocket:
    def __init__(self, url):
        self.url = url
        self.ws = None

    def on_open(self, ws):
        print("Opened connection")
        subscribe = {"method": "SUBSCRIBE", "params": ["btcusdt@kline_1s"], "id": 1}
        ws.send(json.dumps(subscribe))

    def on_message(self, ws, message):
        data = json.loads(message)
        json_data = json.dumps(
                {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "value": data["k"]["c"],
                }
            )
        print(json_data)

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws):
        print("Connection closed")

    def start(self):
        try:
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )
            self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            print(f"An exception occurred: {e}")
        finally:
            if self.ws is not None:
                self.ws.close()

if __name__ == "__main__":
    url = "wss://stream.binance.com:9443/ws"
    binance_ws = BinanceWebSocket(url)
    binance_ws.start()
