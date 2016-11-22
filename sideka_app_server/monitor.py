from flask import Flask, request,jsonify, render_template, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from phpass import PasswordHash
import MySQLdb
import os
import json
import time


app = Flask(__name__, static_url_path='')
mysql = MySQL(app)

# MySQL configurations
app.config.from_pyfile('app.cfg')

phasher = PasswordHash(8, True)


@app.route('/')
def index():
	return render_template('desa.html')

@app.route('/contents')
def contents():
	return render_template('contents.html')

@app.route('/statics/<path:path>')
def send_statics(path):
	return send_from_directory('statics', path)


@app.route('/api/desa', methods=["GET"])
def get_all_desa():
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = "SELECT * from sd_desa"
		cur.execute(query)
		desa = list(cur.fetchall())
		return jsonify(desa)
	finally:
		cur.close()

@app.route('/api/contents', methods=["GET"])
def get_contents():
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = "SELECT sd_contents.id, desa_id, d.desa, type, subtype, timestamp, date_created, created_by, u.user_login, opendata_date_pushed, opendata_push_error from sd_contents left join sd_desa d on desa_id = d.blog_id left join wp_users u on u.ID = created_by order by date_created desc limit 1000"
		cur.execute(query)
		contents = list(cur.fetchall())
		return jsonify(contents)
	finally:
		cur.close()


if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["MONITOR_PORT"])

