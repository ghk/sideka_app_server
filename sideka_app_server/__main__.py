from flask import Flask, request,jsonify
from flask_mysqldb import MySQL
from phpass import PasswordHash
import os


app = Flask(__name__)
mysql = MySQL(app)

# MySQL configurations
app.config.from_pyfile('app.cfg')

phasher = PasswordHash(8, True)


@app.route('/login', methods=["POST"])
def login():
	login = request.json

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
			cur.execute("INSERT INTO sd_tokens VALUES ('%s', %d, now())"  % (token, user[0]))
			mysql.connection.commit()

	cur.close();

	return jsonify({'success': success, 'desa_id': desa_id, 'desa_name': desa_name, 'token': token , 'user_id': user[0], 'user_nicename': user[2]})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

