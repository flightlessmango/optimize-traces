#!/usr/bin/env python3
import os
import valvetraces

from flask import Flask

app = Flask(__name__)

@app.route("/")
def listen():
    username = os.environ.get("VALVETRACESUSER", None)
    password = os.environ.get("VALVETRACESPASS", None)
    client = valvetraces.Client("http://crazett.com", username, password)
    return client.optimize_trace()