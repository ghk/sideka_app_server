from flask import Flask, request,jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from phpass import PasswordHash
import MySQLdb
import os
import json
import time


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

#new data api
@app.route('/content_new/<int:desa_id>/<content_type>', methods=["GET"])
@app.route('/content_new/<int:desa_id>/<content_type>/<content_subtype>', methods=["GET"])
def get_content_new(desa_id, content_type, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		user_id = get_auth(desa_id, cur)
		result = None
		
		if user_id is None:
			return jsonify({}), 403
		
		changeId = int(request.args.get("changeId", "0"))
		query = "SELECT content, change_id FROM sd_contents WHERE desa_id = %s AND type = %s AND subtype = %s AND change_id > %s ORDER BY change_id DESC"

		if content_subtype is None:
			query = "SELECT content, change_id FROM sd_contents WHERE desa_id = %s AND type = %s AND subtype is %s AND change_id > %s ORDER BY change_id DESC"
		
		cur.execute(query, (desa_id, content_type, content_subtype, changeId))
		content = cur.fetchone()
		
		if content is None:
			return jsonify({}), 404
		
		result = json.loads(content[0])

		if changeId > 0:
			return jsonify({"changeId": content[1], "diffs": result["diffs"] })

		return jsonify({"changeId": content[1], "content": result })
	finally:
		cur.close()

@app.route('/content_new/<int:desa_id>/<content_type>', methods=["POST"])
@app.route('/content_new/<int:desa_id>/<content_type>/<content_subtype>', methods=["POST"])
def post_content_new(desa_id, content_type, content_subtype=None):
	cur = mysql.connection.cursor()
	try:
		success = False
		user_id = get_auth(desa_id, cur)

		if user_id is None:
			return jsonify({'success': False}), 403

		changeId = int(request.args.get("changeId", "0"))
		content = merge_diffs(changeId, desa_id, content_type, content_subtype, request.json["diffs"], request.json["columns"])
		
		if content_subtype != "subtypes":
			cur.execute("INSERT INTO sd_contents(desa_id, type, subtype, content, date_created, created_by, change_id) VALUES(%s, %s, %s, %s, now(), %s, %s)", (desa_id, content_type, content_subtype, json.dumps(content), user_id, changeId + 1))
			mysql.connection.commit()
			logs(user_id, desa_id, "", "save_content", content_type, content_subtype)

		suceess = True
		return jsonify({"success": True, "changeId": changeId + 1 })
	finally:
		cur.close()

def merge_diffs(changeId, desaId, type, subtype, diffs, columns):
	cur = mysql.connection.cursor()
	query = "SELECT content FROM sd_contents WHERE desa_id = %s AND type = %s AND subtype = %s AND change_id = %s ORDER BY change_id DESC"

	if subtype is None:
		query = "SELECT content FROM sd_contents WHERE desa_id = %s AND type = %s AND subtype is %s AND change_id = %s ORDER BY change_id DESC"

	cur.execute(query, (desaId, type, subtype, changeId))
	content = cur.fetchone()
	data = json.loads(content[0])
	result = { "columns": columns, "diffs": diffs, "data": data["data"] }

	for diff in diffs:
		for modified in diff["modified"]:
			for server in result["data"]:
				if modified[0] == server[0]:
					for i in modified:
						result["data"][i] = modified[i]	
		for added in diff["added"]:
			for server in data["data"]:
				if added[0] == server[0]:
					for i in added:
						result["data"][i] = added[i]	
		for deleted in diff["deleted"]:
			for server in data["data"]:
				if deleted[0] == server[0] and deleted[1] == server[1]:
					result["data"].remove(server)
					
	return result

if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["PORT"])
