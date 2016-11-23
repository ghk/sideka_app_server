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
	return render_template('desa.html', active='desa')

@app.route('/contents')
def contents():
	return render_template('contents.html', active='contents')

@app.route('/code_finder')
def code_finder():
	return render_template('code_finder.html', active='code_finder')

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

@app.route('/api/desa', methods=["POST"])
def update_desa():
	blog_id = int(request.form.get('blog_id'))
	column = str(request.form.get('column'))
	value = str(request.form.get('value'))
	print blog_id, column, value
	allowedColumns = ["kode", "latitude", "longitude", "sekdes", "kades"];
	if column not in allowedColumns:
		return

	if column in ["latitude", "longitude"]:
		value = float(value)

	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = "UPDATE sd_desa set "+column+" = %s where blog_id = %s"
		cur.execute(query, (value, blog_id))
		mysql.connection.commit()
		return jsonify({'success': True})
	finally:
		cur.close()

@app.route('/api/update_desa_from_code', methods=["POST"])
def update_desa_from_code():
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = """
		update
		sd_desa d
	left join  sd_all_desa desa on d.kode = desa.region_code
	left join  sd_all_desa kec on desa.parent_code = kec.region_code
	left join  sd_all_desa kab on kec.parent_code = kab.region_code
	left join  sd_all_desa prop on kab.parent_code = prop.region_code
		set d.desa = desa.region_name,
			d.kecamatan = kec.region_name,
			d.kabupaten = kab.region_name,
			d.propinsi = prop.region_name
	where trim(coalesce(d.kode, '')) <> ''
		"""
		cur.execute(query)
		mysql.connection.commit()
		return jsonify({'success': True})
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

@app.route('/api/find_all_desa', methods=["GET"])
def find_all_desa():
	q = str(request.args.get('q')).lower() 
	print q
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = "SELECT d.region_code, d.region_name as desa, kec.region_name as kecamatan, kab.region_name as kabupaten, prop.region_name as propinsi from sd_all_desa d left join sd_all_desa kec on d.parent_code = kec.region_code left join sd_all_desa kab on kec.parent_code = kab.region_code left join sd_all_desa prop on kab.parent_code = prop.region_code where lower(d.region_name) like %s and d.depth = 4 limit 100"
		cur.execute(query, (q,))
		results = list(cur.fetchall())
		return jsonify(results)
	finally:
		cur.close()

if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["MONITOR_PORT"])

