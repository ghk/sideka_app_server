from flask import Flask, request,jsonify
from flask_mysqldb import MySQL
from phpass import PasswordHash
import os
import json


app = Flask(__name__)
mysql = MySQL(app)

# MySQL configurations
app.config.from_pyfile('app.cfg')

phasher = PasswordHash(8, True)


@app.route('/login', methods=["POST"])
def login():
	login = request.json
	print login

	cur = mysql.connection.cursor()
	cur.execute("SELECT ID, user_pass, user_nicename FROM wp_users where user_login = %s or user_email = %s", (login["user"], login["user"]))
	user = cur.fetchone()

	success = False
	token = None
	desa_id = 0
	desa_name = None

	if user is not None:
		success = phasher.check_password(login["password"], user[1])

		if success: 
			cur.execute("SELECT meta_value FROM wp_usermeta where user_id = %d and meta_key = 'primary_blog'" % user[0])
			primary_blog = cur.fetchone()
			if primary_blog is not None:
				desa_id = int(primary_blog[0])
				cur.execute("SELECT option_value FROM wp_%d_options where option_name = 'blogname'" % desa_id)
				opt = cur.fetchone()
				if opt is not None:
					desa_name = opt[0]

			token = os.urandom(64).encode('base64')
			cur.execute("INSERT INTO sd_tokens VALUES ('%s', %d, %d, now())"  % (token, user[0], desa_id))
			mysql.connection.commit()

	cur.close();

	return jsonify({'success': success, 'desa_id': desa_id, 'desa_name': desa_name, 'token': token , 'user_id': user[0], 'user_nicename': user[2]})

def get_auth(desa_id, cur):
	token = request.headers.get('X-Auth-Token', None)
	if token is not None:
		cur.execute("SELECT user_id FROM sd_tokens where token = %s or desa_id = %s", (token, desa_id))
		user = cur.fetchone()
		if user is not None:
			return user[0]

	return None

@app.route('/content/<int:desa_id>/<content_type>', methods=["POST"])
def post_content(desa_id, content_type):
	cur = mysql.connection.cursor()
	success = False
	user_id = get_auth(desa_id, cur)

	if user_id is not None:
		timestamp = request.json["timestamp"]
		print request.data	
		cur.execute("INSERT INTO sd_contents VALUES (%s, %s, %s, %s, now(), %s)",   (desa_id, content_type, request.data, timestamp, user_id))
		mysql.connection.commit()
		success = True

	cur.close()
	return jsonify({'success': success, 'user_id': user_id})

@app.route('/content/<int:desa_id>/<content_type>', methods=["GET"])
def get_content(desa_id, content_type):
	cur = mysql.connection.cursor()
	user_id = get_auth(desa_id, cur)
	result = None
	success = False

	if user_id is not None:
		timestamp = int(request.args.get('timestamp', "0"))
		cur.execute("SELECT content from sd_contents where desa_id = %s and timestamp > %s order by timestamp desc",   (desa_id, timestamp))
		content = cur.fetchone()
		if content is not None:
			success = True
			result = json.loads(content[0])
			cur.close()
			return jsonify(result)
	cur.close()
	return jsonify({}), 400



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

