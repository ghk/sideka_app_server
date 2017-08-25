import sys
sys.path.append('../common')

from flask import Flask, send_from_directory
import os, json

app = Flask(__name__)
app.secret_key = app.config["SECRET_KEY"]
app.config.from_pyfile('../common/app.cfg')
BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_FOLDER = os.path.join(BASE_URL, "client")

if __name__ == "__main__":
    app.run(debug=True, host=app.config["HOST"], port=app.config["TATAKELOLA_PORT"])