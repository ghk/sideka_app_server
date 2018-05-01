import sys
import os, logging

moddir = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
sys.path.append(moddir)

from logging.handlers import RotatingFileHandler
from tatakelola_kabupaten import create_app

app = create_app()

if __name__ == "__main__":
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'tatakelola-kabupaten.log')
    handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.run(debug=True, host=app.config["HOST"], port=app.config["TATAKELOLA_KABUPATEN_PORT"])
