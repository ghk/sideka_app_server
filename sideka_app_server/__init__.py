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
		return jsonify({'success': success, 'desa_id': desa_id, 'desa_name': desa_name, 'token': token , 'user_id': user_id, 'user_nicename': user_nicename, 'api_version': app.config["API_VERSION"]})
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
	print(token)
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
@app.route('/content/<int:desa_id>/<content_type>', methods=["GET"])
@app.route('/content/<int:desa_id>/<content_type>/<content_subtype>', methods=["GET"])
def get_content(desa_id, content_type, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		result = None
		print(desa_id)
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
		result = json.loads(content)
		
		return jsonify(result)

	finally:
		cur.close()
@app.route('/content/<int:desa_id>/<content_type>', methods=["POST"])
@app.route('/content/<int:desa_id>/<content_type>/<content_subtype>', methods=["POST"])
def post_content(desa_id, content_type, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		success = False
		user_id = get_auth(desa_id, cur)
		api_version = app.config["API_VERSION"]
        
		cur.execute("SELECT COUNT(*) FROM sd_contents WHERE desa_id = %s AND type = %s AND api_version = %s", (desa_id, content_type, api_version))
		new_data_api = int(cur.fetchone()[0])

		if new_data_api > 0:
			return jsonify({"error": "Sideka needs to be updated"}), 500

		if user_id is None:
			return jsonify({'success': False}), 403
		
		max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s"

		if content_subtype is None:
			max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s"
		
		cur.execute(max_change_id_query, (content_type, content_subtype, desa_id))
		cur_fetch_max_change_id = cur.fetchone()

		if cur_fetch_max_change_id is None:
			return jsonify({}), 404
		
		max_change_id = int(cur_fetch_max_change_id[0])

		if content_subtype != "subtypes":  
			new_change_id = max_change_id + 1;         
			timestamp = int(request.json["timestamp"])
			server_timestamp = int(time.time() * 1000)
			print "%d - %d = %d" % (timestamp, server_timestamp, timestamp - server_timestamp)
			if timestamp > server_timestamp or timestamp <= 0:
				print "reseting to server timestamp, diff: %d" % (server_timestamp - timestamp)
				timestamp = server_timestamp
			cur.execute("INSERT INTO sd_contents (desa_id, type, subtype, content, timestamp, date_created, created_by, change_id) VALUES (%s, %s, %s, %s, %s, now(), %s, %s)",   (desa_id, content_type, content_subtype, request.data, timestamp, user_id, new_change_id))
			mysql.connection.commit()
			logs(user_id, desa_id, "", "save_content", content_type, content_subtype)

			success = True
		return jsonify({'success': success})
	finally:
		cur.close()
@app.route('/content/2.0/<int:desa_id>/<content_type>/<key>', methods=["GET"])
@app.route('/content/2.0/<int:desa_id>/<content_type>/<key>/<content_subtype>', methods=["GET"])
def get_content_v2(desa_id, content_type, key, content_subtype=None):
    cur = mysql.connection.cursor()
    result = None
    try:
        user_id = get_auth(desa_id, cur)
        change_id = int(request.args.get("changeId", "0"))

        if user_id is None:
			return jsonify({}), 403
		
        content_query = "SELECT content, change_id FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s AND change_id >=%s ORDER BY change_id DESC"
        
        if content_subtype is None:
            content_query = "SELECT content, change_id FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s AND change_id >=%s ORDER BY change_id DESC"
      
        cur.execute(content_query, (content_type, content_subtype, desa_id, change_id))
        cur_fetch = cur.fetchone()
		
        if cur_fetch is None:
            return jsonify({}), 404
        
        bundle_data = json.loads(cur_fetch[0])

        diffs = {}
        diffs[key] = []
		
	if bundle_data.has_key("diffs") == False:	
		return jsonify({"change_id": cur_fetch[1], "data": bundle_data["data"] })
					
    
        if bundle_data["diffs"].has_key(key):
            diffs[key] = bundle_data["diffs"][key]
        
        if change_id > 0:
            return jsonify({"change_id": cur_fetch[1], "diffs": diffs[key] })
        
        return jsonify({"change_id": cur_fetch[1], "data": bundle_data["data"] })
    finally:
        cur.close()

@app.route('/content/2.0/<int:desa_id>/<content_type>/<key>', methods=["POST"])
@app.route('/content/2.0/<int:desa_id>/<content_type>/<key>/<content_subtype>', methods=["POST"])
def post_content_v2(desa_id, content_type, key, content_subtype=None):
    cur = mysql.connection.cursor()
   
    try:
		user_id = get_auth(desa_id, cur)
		current_change_id = int(request.args.get("changeId", 0))
		result = None

		if user_id is None or current_change_id is None:
			return jsonify({}), 403
		
		max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s"

		if content_subtype is None:
			max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s"
		
		cur.execute(max_change_id_query, (content_type, content_subtype, desa_id))
		cur_fetch_max_change_id = cur.fetchone()

		if cur_fetch_max_change_id is None:
			return jsonify({}), 404
		
		max_change_id = int(cur_fetch_max_change_id[0])

		latest_content_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s AND change_id > %s ORDER BY change_id ASC"

		if content_subtype is None:
			latest_content_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s AND change_id > %s ORDER BY change_id ASC"
		
		cur.execute(latest_content_query, (content_type, content_subtype, desa_id, current_change_id))
		cur_fetch_latest_contents = cur.fetchall()

		diffs = {}
		diffs[key] = []

		for cur_fetch_latest_content in cur_fetch_latest_contents:
			latest_content = json.loads(cur_fetch_latest_contents[0])
			if latest_content.has_key("diffs") == False:
				continue
			
			if latest_content["diffs"].has_key(key):
				for diff in latest_content["diffs"][key]:
						diffs[key].append(diff)
		
		if content_subtype != 'subtype':
			new_change_id = max_change_id + 1
			current_content_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s AND change_id=%s"

			if content_subtype is None:
				current_content_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s AND change_id=%s"
			
			cur.execute(current_content_query, (content_type, content_subtype, desa_id, current_change_id))
			cur_fetch_current_content = cur.fetchone()	

			if cur_fetch_current_content is None:
				return jsonify({}), 404
			
			current_content = json.loads(cur_fetch_current_content[0])
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
					if isinstance(current_content[content_key], dict):
						data_keys = current_content[content_key].keys()
						for content_data_key in data_keys:
							if content_data_key != key:
								new_content["data"][content_data_key] = current_content["data"][content_data_key]
								new_content["columns"][content_data_key] = current_content["columns"][content_data_key]

			json_new_content = json.dumps(new_content)
			cur.execute("INSERT INTO sd_contents(desa_id, type, subtype, content, date_created, created_by, change_id, api_version) VALUES(%s, %s, %s, %s, now(), %s, %s, %s)", (desa_id, content_type, content_subtype, json_new_content, user_id, new_change_id, '2.0'))
			mysql.connection.commit()
			logs(user_id, desa_id, "", "save_content", key, content_subtype)
			suceess = True
			return jsonify({"success": True, "change_id": new_change_id, "diffs": diffs[key] })
    finally:
        cur.close()

@app.route('/content-map/<int:desa_id>', methods=["GET"])
@app.route('/content-map/<int:desa_id>/<int:change_id>', methods=["GET"])
def get_map_content(desa_id, change_id = None):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		result = None
		
		if user_id is None:
			return jsonify({}), 403
		
		if change_id is None:
			change_id = 0

		content_query = "SELECT content, change_id FROM sd_contents where type='map' AND desa_id=%s AND change_id >= %s ORDER BY change_id DESC"
		cur.execute(content_query, (desa_id, change_id))
		cur_bundle_data = cur.fetchone()
			
		if cur_bundle_data is None:
			return jsonify({}), 404
		
		bundle_data = json.loads(cur_bundle_data[0])

		diffs = []

		if bundle_data.has_key("diffs"):
			diffs = bundle_data["diffs"]

		if change_id > 0:
			return jsonify({"change_id": cur_bundle_data[1], "diffs": diffs })	

		return jsonify({"change_id": cur_bundle_data[1], "center": bundle_data["center"], "data": bundle_data["data"] })
	finally:
		cur.close()

@app.route('/content-map/<int:desa_id>', methods=["POST"])
@app.route('/content-map/<int:desa_id>/<int:change_id>', methods=["POST"])
def post_map_content(desa_id, change_id = None):
	 cur = mysql.connection.cursor()
	 try:
		user_id = get_auth(desa_id, cur)
		result = None
		
		if user_id is None:
			return jsonify({}), 403
		
		max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type='map' AND desa_id=%s"
		cur.execute(max_change_id_query, (desa_id, ))
		cur_fetch_max_change_id = cur.fetchone()

		if cur_fetch_max_change_id is None:
			return jsonify({}), 404
		
		max_change_id = int(cur_fetch_max_change_id[0])
		latest_content_query = "SELECT content FROM sd_contents WHERE type='map' AND desa_id=%s AND change_id > %s ORDER BY change_id ASC"
		cur.execute(latest_content_query, (desa_id, change_id))
		cur_fetch_latest_contents = cur.fetchall()
		diffs = []

		for cur_fetch_latest_content in cur_fetch_latest_contents:
			latest_content = json.loads(cur_fetch_latest_contents[0])

			if latest_content.has_key("diffs") == False:
				continue
			
			diffs.append(latest_content["diffs"])
		
		new_change_id = max_change_id + 1
		current_content_query = "SELECT content FROM sd_contents WHERE type='map' AND desa_id=%s AND change_id=%s"
		cur.execute(current_content_query, (desa_id, change_id))
		cur_fetch_current_content = cur.fetchone()	

		if cur_fetch_current_content is None:
			return jsonify({}), 404
			
		current_content = json.loads(cur_fetch_current_content[0])
		new_content = {"changeId": new_change_id, "center": current_content["center"], "data": [], "diffs": request.json["diffs"]}
		new_content["data"] = merge_map_diffs(new_content["diffs"], current_content["data"])
		json_new_content = json.dumps(new_content)
		cur.execute("INSERT INTO sd_contents(desa_id, type, subtype, content, date_created, created_by, change_id) VALUES(%s, %s, %s, %s, now(), %s, %s)", (desa_id, 'map', None, json_new_content, user_id, new_change_id))
		mysql.connection.commit()
		suceess = True
		return jsonify({"success": True, "change_id": new_change_id, "diffs": diffs })
	 finally:
		 cur.close()

def merge_diffs(diffs, data):
	for diff in diffs:
		for added in diff["added"]:
			data.append(added)
		for modified in diff["modified"]:
			for index, item in enumerate(data):
				if item[0] == modified[0] or len(item[0]) != len(modified[0]):
					data[index] = modified
					break
		for deleted in diff["deleted"]:
			for item in data:
				if item[0] == deleted[0] or len(item[0]) != len(modified[0]):
					data.remove(data)
	return data

def merge_map_diffs(diffs, data):
	for diff in diffs:
		for added in diff["added"]:
			data.append(added)
		for modified in diff["modified"]:
			for index, item in enumerate(data):
				if item["id"] == modified["id"]:
					data[index] = modified
					
					break
		for deleted in diff["deleted"]:
			for item in data:
				if item["id"] == deleted["id"]:
					data.remove(data)
	return data
if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["PORT"])