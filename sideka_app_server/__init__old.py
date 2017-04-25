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

@app.route('/content/<int:desa_id>/<content_type>', methods=["POST"])
@app.route('/content/<int:desa_id>/<content_type>/<content_subtype>', methods=["POST"])
def post_content(desa_id, content_type, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		success = False
		user_id = get_auth(desa_id, cur)

		if user_id is None:
			return jsonify({'success': False}), 403

		if content_subtype != "subtypes":
			timestamp = int(request.json["timestamp"])
			server_timestamp = int(time.time() * 1000)
			print "%d - %d = %d" % (timestamp, server_timestamp, timestamp - server_timestamp)
			if timestamp > server_timestamp or timestamp <= 0:
				print "reseting to server timestamp, diff: %d" % (server_timestamp - timestamp)
				timestamp = server_timestamp
			cur.execute("INSERT INTO sd_contents (desa_id, type, subtype, content, timestamp, date_created, created_by) VALUES (%s, %s, %s, %s, %s, now(), %s)",   (desa_id, content_type, content_subtype, request.data, timestamp, user_id))
			mysql.connection.commit()
			logs(user_id, desa_id, "", "save_content", content_type, content_subtype)

			success = True
		return jsonify({'success': success})
	finally:
		cur.close()

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

@app.route('/content/<int:desa_id>/<content_type>', methods=["GET"])
@app.route('/content/<int:desa_id>/<content_type>/<content_subtype>', methods=["GET"])
def get_content(desa_id, content_type, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		result = None

		if user_id is None:
			return jsonify({}), 403

		timestamp = int(request.args.get('timestamp', "0"))
		query = "SELECT content from sd_contents where desa_id = %s and timestamp > %s and type = %s and subtype = %s order by timestamp desc"
		if content_subtype is None:
			query = "SELECT content from sd_contents where desa_id = %s and timestamp > %s and type = %s and subtype is %s order by timestamp desc"
		cur.execute(query, (desa_id, timestamp, content_type, content_subtype))
		content = cur.fetchone()
		if content is None:
			return jsonify({}), 404

		logs(user_id, desa_id, "", "get_content", content_type, content_subtype)
		result = json.loads(content[0])
		return jsonify(result)

	finally:
		cur.close()
	

@app.route('/desa', methods=["GET"])
@cross_origin()
def get_all_desa():
	cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	try:
		query = "SELECT * from sd_desa"
		cur.execute(query)
		desa = list(cur.fetchall())
		return jsonify(desa)
	finally:
		cur.close()

@app.route('/v2/update_data_structure/<int:desa_id>/<content_type>', methods=["POST"])
@app.route('/v2/update_data_structure/<int:desa_id>/<content_type>/<content_subtype>', methods=["POST"])
def update_data_structure(desa_id, content_type, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		result = None

		if user_id is None:
			return jsonify({}), 403
		
		change_id = int(request.args.get("changeId", "0"))
		new_bundle_structure = json.dumps(request.json["bundle"])
		cur.execute("UPDATE sd_contents SET content = %s WHERE desa_id = %s AND type = %s AND change_id = %s", (new_bundle_structure, desa_id, content_type, change_id))
		mysql.connection.commit()
		return jsonify({"success": True })
	finally:
		cur.close()

@app.route('/v2/content/<int:desa_id>/<content_type>', methods=["GET"])
@app.route('/v2/content/<int:desa_id>/<content_type>/<content_subtype>', methods=["GET"])
def get_content_v2(desa_id, content_type, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		result = None

		if user_id is None:
			return jsonify({}), 403
		
		change_id = int(request.args.get("changeId", "0"))
		diff_type = request.args.get("diffType")

		content_query = "select content, change_id from sd_contents where type=%s and subtype=%s and desa_id=%s and change_id >= %s order by change_id desc"

		if content_subtype is None:
			content_query = "select content, change_id from sd_contents where type=%s and subtype is %s and desa_id=%s and change_id >= %s order by change_id desc"
		
		cur.execute(content_query, (content_type, content_subtype, desa_id, change_id))

		content_data = cur.fetchone()

		if content_data is None:
			return jsonify({}), 404

		content_data_json = json.loads(content_data[0])

		diffs = {}
		diffs[content_type] = []

		if content_data_json.has_key("diffs"):
			if isinstance(content_data_json["diffs"], list):
				diffs[content_type] = content_data_json["diffs"]
			else:
				if content_data_json["diffs"].has_key(content_type):
					diffs[content_type] = content_data_json["diffs"][diff_type]
			
		if change_id > 0:
			return jsonify({"change_id": content_data[1], "diffs": diffs[diff_type] })
		
		return jsonify({"change_id": content_data[1], "data": content_data_json["data"] })
	finally:
		cur.close()
	
@app.route('/v2/content/<int:desa_id>/<content_type>', methods=["POST"])
@app.route('/v2/content/<int:desa_id>/<content_type>/<content_subtype>', methods=["POST"])
def post_content_v2(desa_id, content_type, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		current_change_id = int(request.args.get("changeId", 0))
		diff_type = request.args.get("diffType");
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

		newest_contents_query = "select content from sd_contents where type=%s and subtype=%s and desa_id=%s and change_id > %s order by change_id asc"

		if content_subtype is None:
			newest_contents_query = "select content from sd_contents where type=%s and subtype is %s and desa_id=%s and change_id>%s order by change_id asc"
		
		cur.execute(newest_contents_query, (content_type, content_subtype, desa_id, current_change_id))

		newest_contents = cur.fetchall()
		content_type_diffs = {}
		content_type_diffs[diff_type] = []

		for newest_content in newest_contents:
			diffs = json.loads(newest_content[0])["diffs"]
	
			if diffs.has_key(diff_type):
				diffs = diffs[diff_type]
			
			for diff in diffs:
				content_type_diffs[diff_type].append(diff)
		
		if content_subtype != 'subtype':
			new_change_id = int_max_change_id + 1
			content_query = "select content from sd_contents where type=%s and subtype=%s and desa_id=%s and change_id=%s"

			if content_subtype is None:
				content_query = "select content from sd_contents where type=%s and subtype is %s and desa_id=%s and change_id=%s"
			
			cur.execute(content_query, (content_type, content_subtype, desa_id, current_change_id))

			content = cur.fetchone()

			if content is None:
				return jsonify({}), 404

			content_json = json.loads(content[0])
			content_type_data = []
			content_type_columns = []
			
			if isinstance(content_json["data"], list):
				content_type_data = content_json["data"]
			else:
				if content_json["data"].has_key(diff_type):
					content_type_data = content_json["data"][diff_type]
				
			if isinstance(content_json["columns"], list):
				content_type_columns = content_json["columns"]
			else:
				if content_json["columns"].has_key(diff_type):
					content_type_columns = content_json["columns"][diff_type]
				else:
					content_type_columns = content_json["columns"]
			
			if content_type_data is None:
				content_type_data = []
			
			merged_data = merge_diffs(request.json["diffs"], content_type_data)
		
			new_bundle = { "columns": {}, "data": {}, "diffs": content_json["diffs"], "changeId": new_change_id }
			new_bundle["diffs"][diff_type] = request.json["diffs"]
			new_bundle["columns"][diff_type] = content_type_columns
			new_bundle["data"][diff_type] = merged_data
			new_bundle_dumps = json.dumps(new_bundle)

			cur.execute("INSERT INTO sd_contents(desa_id, type, subtype, content, date_created, created_by, change_id) VALUES(%s, %s, %s, %s, now(), %s, %s)", (desa_id, content_type, content_subtype, new_bundle_dumps, user_id, new_change_id))
			mysql.connection.commit()
			logs(user_id, desa_id, "", "save_content", diff_type, content_subtype)
			suceess = True
			return jsonify({"success": True, "change_id": new_change_id, "diffs": content_type_diffs[diff_type] })
	finally:
		cur.close()

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