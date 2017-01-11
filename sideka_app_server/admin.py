from flask import Flask, request,jsonify, render_template, send_from_directory, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from phpass import PasswordHash
import MySQLdb
import os
import json
import urllib
import time
import datetime
import logging
from utils import open_cfg


app = Flask(__name__, static_url_path='')
mysql = MySQL(app)
# MySQL configurations
app.config.from_pyfile('app.cfg')

phasher = PasswordHash(8, True)
app.secret_key = app.config["SECRET_KEY"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"


class User(UserMixin):
	pass

def check_account(email):
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		cur.execute("SELECT ID, user_pass, user_nicename FROM wp_users where user_login = %s or user_email = %s", (email, email))
		user = cur.fetchone()
		return user
	finally:
		pass	

@login_manager.user_loader
def user_loader(email):
	userMix = User()
	userMix.id = email
	return userMix
	
@login_manager.request_loader
def request_loader(request):
	email = request.form.get('email')
	user = check_account(email)
	success = False
	if user is not None:
		userMix = User()
		userMix.id = email
		success = phasher.check_password(request.form['pw'], user['user_pass'])
		if success:
			userMix.is_authenticated = success
			return userMix
		else:
			return
	else:
		return
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':   
		email = request.form.get('email')     
		user = check_account(email)
		success = False
		if user is not None:
			success = phasher.check_password(request.form['pw'], user['user_pass'])
			if success:
				usermix = User()
				usermix.id = email
				login_user(usermix)
				return redirect('/')
    return render_template('admin/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))


@app.route('/')
@login_required
def desa():
	return render_template('admin/desa.html', active='desa')

@app.route('/contents')
def contents():
	return render_template('admin/contents.html', active='contents', now = datetime.datetime.now())

@app.route('/code_finder')
def code_finder():
	return render_template('admin/code_finder.html', active='code_finder')

@app.route('/contents/<int:content_id>')
def contents_single(content_id):
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = "SELECT desa_id, subtype, type, content from sd_contents where id = %s"
		cur.execute(query, (content_id,))
		result = cur.fetchone()
		content = result["content"]
		typ = result["type"]
		subtyp = result["subtype"]
		desa_id = result["desa_id"]
		schema_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "schemas/"+typ+".json")
		print schema_file
		with open(schema_file, 'r') as myfile:
		    schema=myfile.read()
		return render_template('admin/contents_single.html', active='contents', content=content, schema=schema, subtyp=subtyp, typ=typ, desa_id = desa_id)
	finally:
		cur.close()

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
	allowedColumns = ["kode", "latitude", "longitude", "sekdes", "kades", "pendamping"];
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

@app.route('/api/update_sd_desa', methods=["POST"])
def update_sd_desa():
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = """
			INSERT INTO sd_desa (blog_id, domain) SELECT blog_id, domain FROM wp_blogs WHERE blog_id > (select max(blog_id) from sd_desa)
		"""
		cur.execute(query)
		query = """
			UPDATE sd_desa as d inner join wp_blogs b on d.blog_id = b.blog_id set d.domain = b.domain
		"""
		cur.execute(query)
		mysql.connection.commit()
		return jsonify({'success': True})
	finally:
		cur.close()

@app.route('/api/geocode_empty_latlong', methods=["POST"])
def geocode_empty_latlong():
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = """
			select blog_id, desa, kecamatan, kabupaten from sd_desa where latitude is null and longitude is null and (kode is not null and kode <> '')
		"""
		cur.execute(query)
		desas = list(cur.fetchall())
		results = []
		for desa in desas:
			address = (desa['desa']+', '+desa['kecamatan']+", "+desa['kabupaten']).replace(' ', '+')
			url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=AIzaSyATCm-ki0JV9hjtjQXOKvqwlMaBWpYByEc" % address
			results.append(url)
			response = urllib.urlopen(url)
			data = json.loads(response.read())
			if data["status"] == "OK":
				result = data["results"][0]
				latitude = result["geometry"]["location"]["lat"]
				longitude = result["geometry"]["location"]["lng"]
				query = """
					UPDATE sd_desa set latitude = %s, longitude = %s where blog_id = %s
				"""
				cur.execute(query, (latitude, longitude, desa['blog_id']))
				mysql.connection.commit()
			else:
				results.append("%s: not found" % (address,))
		return jsonify(results)
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

@app.route('/api/statistics', methods=["GET"])
def get_statistics():
	cur = mysql.connection.cursor()
	try:
		query = "SELECT statistics from sd_statistics"
		cur.execute(query)
		results = [json.loads(c[0]) for c in cur.fetchall()]
		return jsonify(results)
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
    app.run(debug=True, host=app.config["HOST"], port=app.config["ADMIN_PORT"])
