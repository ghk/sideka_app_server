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

@app.route('/posts')
def post_scores():
	return render_template('monitor/post_scores.html', active='post_scores')

@app.route('/apbdes')
def apbdes_scores():
	return render_template('monitor/apbdes_scores.html', active='apbdes_scores')


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
		query = "SELECT s.statistics, d.pendamping FROM sd_statistics s \
				 INNER JOIN (SELECT blog_id, max(date) as date FROM sd_statistics GROUP BY blog_id ) \
				 st ON s.blog_id = st.blog_id AND s.date = st.date left JOIN sd_desa d ON s.blog_id = d.blog_id"

		cur.execute(query)
		results = [combine(c) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()

@app.route('/api/post_scores')
def get_post_scores():
	cur = mysql.connection.cursor()
	try:
		query = "SELECT score from sd_post_scores"
		cur.execute(query)
		results = [json.loads(c[0]) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()

@app.route('/api/apbdes_scores')
def get_apbdes_scores():
	cur = mysql.connection.cursor()
	try:
		query = "SELECT score from sd_apbdes_scores"
		cur.execute(query)
		results = [json.loads(c[0]) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()

if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["MONITOR_PORT"])
