from flask import Flask, request,jsonify, render_template, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from phpass import PasswordHash
import MySQLdb
import os
import json
import time
import datetime


app = Flask(__name__, static_url_path='')
mysql = MySQL(app)

# MySQL configurations
app.config.from_pyfile('app.cfg')

phasher = PasswordHash(8, True)


@app.route('/')
def statistics():
	return render_template('monitor/statistics.html', active='statistics')


@app.route('/statics/<path:path>')
def send_statics(path):
	return send_from_directory('statics', path)



@app.route('/api/statistics')
def get_statistics():
	def combine(row):
		res = json.loads(row[0])
		res["pendamping"] = row[1]
		return res

	cur = mysql.connection.cursor()
	try:
		query = "SELECT s.statistics, d.pendamping from sd_statistics s left join sd_desa d on s.blog_id = d.blog_id"
		cur.execute(query)
		results = [combine(c) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()

if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["MONITOR_PORT"])

