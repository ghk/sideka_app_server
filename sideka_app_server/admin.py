from flask import Flask, request,jsonify, render_template, send_from_directory, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from phpserialize import *
from collections import OrderedDict
from StringIO import StringIO
from collections import OrderedDict
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
import re


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

def get_user_by_nickname(nickname):
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = "SELECT ID, user_pass from wp_users where user_login = %s"
		cur.execute(query, (nickname,))
		user = cur.fetchone()
		return user
	finally:
		cur.close()

def get_superadmin_user():
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		cur.execute("SELECT meta_value FROM wp_sitemeta WHERE meta_key = 'site_admins'")
		user = cur.fetchone()
		users = loads(user["meta_value"],array_hook=OrderedDict)
		return users.values()
	finally:
		cur.close

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

@login_manager.user_loader
def user_loader(nickname):
	userMix = User()
	userMix.id = nickname
	return userMix
	
@login_manager.request_loader
def request_loader(request):
	nickname = request.form.get('nickname')
	superadminUsers = get_superadmin_user()
	if nickname in superadminUsers:		
		success = False	
		userMix = User()
		userMix.id = nickname
		user = get_user_by_nickname(nickname)
		success = phasher.check_password(request.form['pw'], user['user_pass'])
		if success:
			userMix.is_authenticated = success		
	return

@app.route('/')
@login_required
def desa():
	users = get_superadmin_user()
	return render_template('admin/desa.html', active='desa')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':   
		nickname = request.form.get('nickname')   		
		superadminUsers = get_superadmin_user()
		if nickname in superadminUsers:
			success = False
			user = get_user_by_nickname(nickname)			
			success = phasher.check_password(request.form['pw'], user['user_pass'])
			if success:
				usermix = User()
				usermix.id = nickname
				login_user(usermix)
				return redirect('/')
	return render_template('admin/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/contents')
@login_required
def contents():
	return render_template('admin/contents.html', active='contents', now = datetime.datetime.now())

@app.route('/code_finder')
@login_required
def code_finder():
	return render_template('admin/code_finder.html', active='code_finder')

@app.route('/user_supradesa')
@login_required
def user_supradesa():
	return render_template('admin/user_supradesa.html', active='user_supradesa')

@app.route('/supradesa')
@login_required
def agregate():
	return render_template('admin/supradesa.html', active='supradesa')

@app.route('/contents/<int:content_id>')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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

@app.route('/api/users_supradesa', methods=["GET"])
@login_required
def get_user_supradesa():
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = "select * from sd_users_supradesa"
		cur.execute(query)
		results = list(cur.fetchall())
		return jsonify(results)
	finally:
		cur.close()


def remove_capabilities_and_userlevel(user_id):
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		capabilities = '%'+ '_capabilities'
		user_level = '%'+ '_user_level'
		query = "DELETE FROM wp_usermeta where meta_key like %s and user_id = %s"
		cur.execute(query,(capabilities,str(user_id)))
		
		query = "DELETE FROM wp_usermeta where meta_key like %s and user_id = %s"
		cur.execute(query,(user_level,str(user_id)))
		mysql.connection.commit()	
	finally:
		cur.close()

@app.route('/api/update_users_supradesa', methods=["POST"])
@login_required
def update_user_supradesa():	
	data = json.loads(request.form.get("data"))
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	
	def get_blogs(region_prefix):
		query = "SELECT blog_id FROM sd_desa WHERE kode like %s"
		cur.execute(query, (region_prefix + '.%',))
		result = list(cur.fetchall())
		return result	
	try:
		for row in data:
			if row["username"] == None or row["id_supradesa"] == None:
				continue

			query = "SELECT ID FROM wp_users WHERE user_login = %s"
			cur.execute(query, (row["username"],))	
			user = cur.fetchone()
			if user == None:
				continue

			query = "SELECT * FROM sd_users_supradesa WHERE username = %s and id_supradesa = %s"
			cur.execute(query, (row["username"],row["id_supradesa"]))
			same = cur.fetchone()
			if same != None:
				continue

			query = "SELECT region_code FROM sd_supradesa WHERE id = %s"
			cur.execute(query, (row["id_supradesa"]))
			code = cur.fetchone()
			if code != None:
				query = "REPLACE INTO sd_users_supradesa (username, id_supradesa,level) VALUES (%s,%s,%s)"
				cur.execute(query, (row["username"],row["id_supradesa"],row["level"]))
				mysql.connection.commit()
				remove_capabilities_and_userlevel(user["ID"])

				blogs_id = get_blogs(code["region_code"])
				for blog_id in blogs_id:					
					role = {"administrator":"10","editor":"7","author":"2","contributor":"1","subscriber":"0"}					
					capabilities = ('wp_'+str(blog_id["blog_id"])+'_capabilities')
					user_level = ('wp_'+str(blog_id["blog_id"])+'_user_level')
					level_value = role[row["level"]]
					role = dumps({row["level"]:1})

					query = """INSERT INTO wp_usermeta (user_id, meta_key,meta_value) VALUES (%s, %s,%s), (%s, %s,%s)"""
					cur.execute(query, (user["ID"],capabilities,role,user["ID"],user_level,level_value))
					mysql.connection.commit()
					
		return jsonify({'success': True})
	finally:
		cur.close()

@app.route('/api/remove_users_supradesa', methods=["POST"])
@login_required
def remove_user_supradesa():
	data = json.loads(request.form.get("data"))
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		
		query = "DELETE FROM sd_users_supradesa WHERE username = %s and id_supradesa = %s"
		cur.execute(query, (data["username"],data["id_supradesa"]))
		mysql.connection.commit()

		query = "SELECT ID from wp_users WHERE user_login = %s"
		cur.execute(query, (data["username"],))
		user = cur.fetchone()
		remove_capabilities_and_userlevel(user["ID"])

		return jsonify({'success': True})
	finally:
		cur.close

@app.route('/api/supradesa', methods=["GET"])
@login_required
def get_supradesa():
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = "select * from sd_supradesa"
		cur.execute(query)
		result = jsonify(cur.fetchall())
		return result
	finally:
		cur.close()

@app.route('/api/save_supradesa', methods=["POST"])
@login_required
def save_supradesa():
	data = json.loads(request.form.get("data"))
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		for row in data:
			query = "REPLACE INTO sd_supradesa (region_code,flag,name,blog_agregate,username,password) VALUES (%s,%s,%s,%s,%s) WHERE id = %s"
			cur.execute(query,(row["region_code"],row["flag"],row["blog_agregate"],row["username"],row["password"],row["id"]))
			mysql.connection.commit()

				#result = jsonify(cur.fetchall())
		return jsonify({'success': True})
	finally:
		cur.close()
		
@app.route('/api/remove_supradesa', methods=["POST"])
@login_required
def remove_supradesa():
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = "REPLACE INTO sd_supradesa"
		cur.execute(query)
		result = jsonify(cur.fetchall())
		return result
	finally:
		cur.close()
		


if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["ADMIN_PORT"])
