import json
import logging
import random
import sys
import time
from datetime import datetime
from typing import Iterator
from wsrealtime import *

from flask import Flask, Response, render_template, request, stream_with_context

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

application = Flask(__name__)
random.seed()  # Initialize the random number generator


@application.route("/")
def index() -> str:
    return render_template("index.html")


def generate_data() -> Iterator[str]:
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr or ""

    try:
        logger.info("Client %s connected", client_ip)
        url = "wss://stream.binance.com:9443/ws"
        binance_ws = BinanceWebSocket(url)
        while True:
            json_data = binance_ws.start()
            yield f"data:{json_data}\n\n"
            time.sleep(1)
    except GeneratorExit:
        logger.info("Client %s disconnected", client_ip)


@application.route("/chart-data")
def chart_data() -> Response:
    json_data = json.dumps(data)
    # response = Response(stream_with_context(generate_data()), mimetype="text/event-stream")
    response = Response(stream_with_context(generate_data()), mimetype="text/event-stream")
    print(response)
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


if __name__ == "__main__":
    application.run(host="0.0.0.0", threaded=True)