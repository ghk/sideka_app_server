from flask import Flask, request,jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from phpass import PasswordHash
import MySQLdb
import os
import json
import time
import base64
import uuid

app = Flask(__name__)
mysql = MySQL(app)

# MySQL configurations
app.config.from_pyfile('app.cfg')

phasher = PasswordHash(8, True)

@app.route('/login', methods=["POST"])
def login():
	login = request.json
	print(login['user'])
	cur = mysql.connection.cursor()
	try:
		cur.execute("SELECT ID, user_pass, user_nicename FROM wp_users where user_login = %s or user_email = %s", (login["user"], login["user"]))
		user = cur.fetchone()

		success = False
		token = None
		desa_id = 0
		desa_name = None
		user_id = None
		user_nicename = None
		
		if user is not None:
			success = phasher.check_password(login["password"], user[1])
			print(user)
			if success:
				user_id = user[0]
				user_nicename = user[2]
				cur.execute("SELECT meta_value FROM wp_usermeta where user_id = %d and meta_key = 'primary_blog'" % user[0])
				primary_blog = cur.fetchone()
				if primary_blog is not None:
					desa_id = int(primary_blog[0])
					cur.execute("SELECT option_value FROM wp_%d_options where option_name = 'blogname'" % desa_id)
					opt = cur.fetchone()
					if opt is not None:
						desa_name = opt[0]

				token = os.urandom(64).encode('hex')
				cur.execute("INSERT INTO sd_tokens VALUES (%s, %s, %s, %s, now())", (token, user[0], desa_id, login["info"]))
				mysql.connection.commit()
				logs(user_id, desa_id, token, "login", None, None)
		return jsonify({'success': success, 'desa_id': desa_id, 'desa_name': desa_name, 'token': token , 'user_id': user_id, 'user_nicename': user_nicename})
	finally:
		cur.close();

def logs(user_id, desa_id, token, action, content_type, content_subtype):
	if(token==""):
		token = request.headers.get('X-Auth-Token', None)
	cur = mysql.connection.cursor()
	print content_type
	cur.execute("INSERT INTO sd_logs (user_id, desa_id, date_accessed, token, action, type, subtype) VALUES (%s, %s, now(), %s, %s, %s, %s)",   (user_id, desa_id, token, action, content_type, content_subtype))
	mysql.connection.commit()
	cur.close();

@app.route('/logout', methods=["GET"])
def logout():
	cur = mysql.connection.cursor()
	try:
		token = request.headers.get('X-Auth-Token', None)
		cur.execute("DELETE FROM sd_tokens where token = %s", (token, ))
		mysql.connection.commit()
	finally:
		cur.close();
	return jsonify({'success': True})

@app.route('/check_auth/<int:desa_id>', methods=["GET"])
def check_auth(desa_id):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		return jsonify({'user_id': user_id})
	finally:
		cur.close();

def get_auth(desa_id, cur):
	token = request.headers.get('X-Auth-Token', None)
	print token
	if token is not None:
		cur.execute("SELECT user_id FROM sd_tokens where token = %s and desa_id = %s", (token, desa_id))
		user = cur.fetchone()
		if user is not None:
			return user[0]

	return None

@app.route('/content/<int:desa_id>/<content_type>/subtypes', methods=["GET"])
def get_content_subtype(desa_id, content_type):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)

		if user_id is None:
			return jsonify({}), 403

		query = "SELECT distinct(subtype) from sd_contents where desa_id = %s and type = %s order by timestamp desc"
		cur.execute(query, (desa_id, content_type))
		content = list(cur.fetchall())
		subtypes = [c[0] for c in content]
		return jsonify(subtypes)
	finally:
		cur.close()
		
@app.route('/content/<int:desa_id>/<content_type>/<key>', methods=["GET"])
@app.route('/content/<int:desa_id>/<content_type>/<key>/<content_subtype>', methods=["GET"])
def get_content(desa_id, content_type, key, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		result = None
		change_id = int(request.args.get("changeId", "0"))
		
		if user_id is None:
			return jsonify({}), 403
		
		content_query = "select content, change_id from sd_contents where type=%s and subtype=%s and desa_id=%s and change_id >= %s order by change_id desc"

		if content_subtype is None:
			content_query = "select content, change_id from sd_contents where type=%s and subtype is %s and desa_id=%s and change_id >= %s order by change_id desc"
		
		cur.execute(content_query, (content_type, content_subtype, desa_id, change_id))
		cur_bundle_data = cur.fetchone()

		if cur_bundle_data is None:
			return jsonify({}), 404
		
		bundle_data = json.loads(cur_bundle_data[0])
		diffs = {}
		diffs[key] = []

		if bundle_data.has_key("diffs"):
			if bundle_data["diffs"].has_key(key):
				diffs[key] = bundle_data["diffs"][key]

		if change_id > 0:
			return jsonify({"change_id": cur_bundle_data[1], "diffs": diffs[key] })	
		
		return jsonify({"change_id": cur_bundle_data[1], "data": bundle_data["data"] })
	finally:
		cur.close()

@app.route('/content/<int:desa_id>/<content_type>/<key>', methods=["POST"])
@app.route('/content/<int:desa_id>/<content_type>/<key>/<content_subtype>', methods=["POST"])
def post_content(desa_id, content_type, key, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		current_change_id = int(request.args.get("changeId", 0))
		result = None

		if user_id is None or current_change_id is None:
			return jsonify({}), 403
		
		q_max_change_id = 'select max(change_id) from sd_contents where type=%s and subtype=%s and desa_id=%s'

		if content_subtype is None:
			q_max_change_id = 'select max(change_id) from sd_contents where type=%s and subtype is %s and desa_id=%s'
		
		cur.execute(q_max_change_id, (content_type, content_subtype, desa_id))
		c_max_change_id = cur.fetchone()

		if c_max_change_id is None:
			return jsonify({}), 404
		else:
			max_change_id = int(c_max_change_id[0])
		
		q_latest_contents = "select content from sd_contents where type=%s and subtype=%s and desa_id=%s and change_id > %s order by change_id asc"

		if content_subtype is None:
			q_latest_contents = "select content from sd_contents where type=%s and subtype is %s and desa_id=%s and change_id>%s order by change_id asc"
		
		cur.execute(q_latest_contents, (content_type, content_subtype, desa_id, current_change_id))

		latest_contents = cur.fetchall()
		diffs = {}
		diffs[key] = []

		for c_content in latest_contents:
			content = json.loads(c_content[0])
			if content.has_key("diffs"):
				if content["diffs"].has_key(key):
					for diff in content["diffs"][key]:
						diffs[key].append(diff)
		
		if content_subtype != 'subtype':
			new_change_id = max_change_id + 1
			q_current_content = "select content from sd_contents where type=%s and subtype=%s and desa_id=%s and change_id=%s"
			
			if content_subtype is None:
				q_current_content = "select content from sd_contents where type=%s and subtype is %s and desa_id=%s and change_id=%s"
			
			cur.execute(q_current_content, (content_type, content_subtype, desa_id, current_change_id))
			c_current_content = cur.fetchone()	

			if c_current_content is None:
				return jsonify({}), 404
			
			current_content = json.loads(c_current_content[0])
			current_content_data = []
			current_content_columns = []
			
			if isinstance(current_content["data"], list) and key == 'penduduk':
				current_content_data = current_content["data"]
			elif isinstance(current_content["data"], dict) and current_content["data"].has_key(key):
				current_content_data = current_content["data"][key]
			
			if isinstance(current_content["columns"], list) and key == 'penduduk':
				current_content_columns = current_content["columns"]
			elif isinstance(current_content["columns"], dict) and current_content["columns"].has_key(key):
				current_content_columns = current_content["columns"][key]
			
			
			if current_content_columns == []:
				current_content_columns = request.json["columns"]

			new_content = {"changeId": new_change_id, "columns": {}, "data": {}, "diffs": {}}
			new_content["columns"][key] = current_content_columns
			new_content["data"][key] = merge_diffs(request.json["diffs"], current_content_data)
			new_content["diffs"][key] = request.json["diffs"]

			if isinstance(current_content["data"], list) and key != "penduduk":
			   new_content["data"]["penduduk"] = current_content["data"]
			
			if isinstance(current_content["columns"], list) and key != "penduduk":
				new_content["columns"]["penduduk"] = current_content["columns"]
			
			if isinstance(current_content["data"], dict) and isinstance(current_content["columns"], dict):
				content_keys = current_content.keys()

				for content_key in content_keys:
					data_keys = current_content[content_key].keys()
					for content_data_key in data_keys:
						if content_data_key != key:
							new_content["data"][content_data_key] = current_content["data"][content_data_key]
							new_content["columns"][content_data_key] = current_content["columns"][content_data_key]

			json_new_content = json.dumps(new_content)
			cur.execute("INSERT INTO sd_contents(desa_id, type, subtype, content, date_created, created_by, change_id) VALUES(%s, %s, %s, %s, now(), %s, %s)", (desa_id, content_type, content_subtype, json_new_content, user_id, new_change_id))
			mysql.connection.commit()
			logs(user_id, desa_id, "", "save_content", key, content_subtype)
			suceess = True
			return jsonify({"success": True, "change_id": new_change_id, "diffs": diffs[key] })
	finally:
		cur.close()
"""		
@app.route('/content/<int:desa_id>/<content_type>/<data_type>', methods=["POST"])
@app.route('/content/<int:desa_id>/<content_type>/<data_type>/<content_subtype>', methods=["POST"])
def post_content(desa_id, content_type, data_type, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		current_change_id = int(request.args.get("changeId", 0))
		result = None

		if user_id is None or current_change_id is None:
			return jsonify({}), 403
		
		max_change_id_query = "select max(change_id) from sd_contents where type=%s and subtype=%s and desa_id=%s"

		if content_subtype is None:
			max_change_id_query = "select max(change_id) from sd_contents where type=%s and subtype is %s and desa_id=%s"
		
		cur.execute(max_change_id_query, (content_type, content_subtype, desa_id))
		max_change_id = cur.fetchone()

		if max_change_id is None:
			return jsonify({}), 404
		else:
			int_max_change_id = int(max_change_id[0])

		latest_bundle_data_query = "select content from sd_contents where type=%s and subtype=%s and desa_id=%s and change_id > %s order by change_id asc"

		if content_subtype is None:
			latest_bundle_data_query = "select content from sd_contents where type=%s and subtype is %s and desa_id=%s and change_id>%s order by change_id asc"
		
		cur.execute(latest_bundle_data_query, (content_type, content_subtype, desa_id, current_change_id))
		latest_bundle_data = cur.fetchall()
		diffs = {}
		diffs[data_type] = []
		d_diffs = []

		for bundle_data in latest_bundle_data:
			c_diffs = json.loads(bundle_data[0])["diffs"]
			if c_diffs.has_key(data_type):
			   d_diffs = c_diffs[data_type]
			for diff in d_diffs:
				diffs[data_type].append(diff)
		
		if content_subtype != 'subtype':
			new_change_id = int_max_change_id + 1
			bundle_data_query = "select content from sd_contents where type=%s and subtype=%s and desa_id=%s and change_id=%s"

			if content_subtype is None:
				bundle_data_query = "select content from sd_contents where type=%s and subtype is %s and desa_id=%s and change_id=%s"
			
			cur.execute(bundle_data_query, (content_type, content_subtype, desa_id, current_change_id))
			bundle_data_cur = cur.fetchone()

			if bundle_data_cur is None:
				return jsonify({}), 404
			
			bundle_data = json.loads(bundle_data_cur[0])
			bundle_data_data = []
			bundle_data_columns = []

			if isinstance(bundle_data["data"], list) and data_type == 'penduduk':
			   bundle_data_data = bundle_data["data"]
			elif isinstance(bundle_data["data"], dict) and bundle_data["data"].has_key(data_type):
			   bundle_data_data = bundle_data["data"][data_type]

			if isinstance(bundle_data["columns"], list) and data_type == 'penduduk':
			   bundle_data_columns = bundle_data["columns"]
			elif isinstance(bundle_data["columns"], dict) and bundle_data["columns"].has_key(data_type):
			   bundle_data_columns = bundle_data["columns"][data_type]
			
			print(bundle_data_data)
			merged_bundle_data_data = merge_diffs(request.json["diffs"], bundle_data_data)
			new_bundle_data = { "columns": {}, "data": {}, "diffs": {}, "changeId": new_change_id }
			new_bundle_data["diffs"][data_type] = request.json["diffs"]
			new_bundle_data["columns"][data_type] = bundle_data_columns
			new_bundle_data["data"][data_type] = merged_bundle_data_data
			new_bundle_dumps = json.dumps(new_bundle_data)
			
			cur.execute("INSERT INTO sd_contents(desa_id, type, subtype, content, date_created, created_by, change_id) VALUES(%s, %s, %s, %s, now(), %s, %s)", (desa_id, content_type, content_subtype, new_bundle_dumps, user_id, new_change_id))
			mysql.connection.commit()
			logs(user_id, desa_id, "", "save_content", data_type, content_subtype)
			suceess = True
			
			return jsonify({"success": True, "change_id": current_change_id, "diffs": [] })
	finally:
		cur.close();
"""
def merge_diffs(diffs, data):
	for diff in diffs:
		for added in diff["added"]:
			data.append(added)
		for modified in diff["modified"]:
			for index, item in enumerate(data):
				if item[0] == modified[0]:
					data[index] = modified
					break
		for deleted in diff["deleted"]:
			for item in data:
				if item[0] == deleted[0]:
					data.remove(data)
	return data
if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["PORT"])