import os
from keuangan import app, db
from keuangan.models import *

BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_FOLDER = os.path.join(BASE_URL, "client")

if __name__ == "__main__":
    db.create_all();
    app.run(debug=True, host=app.config["HOST"], port=app.config["KEUANGAN_PORT"])