import sys

sys.path.append("../common");

from admin import app, db, login_manager
from flask import request, jsonify, render_template, send_from_directory, redirect, url_for
from flask_login import login_user, login_required, current_user, logout_user, UserMixin
from sqlalchemy.orm import load_only, aliased
from sqlalchemy import func

from phpserialize import *
from collections import OrderedDict
from common import PasswordHash
from models import *

import os
import json
import urllib
import datetime

phasher = PasswordHash(8, True)


class User(UserMixin):
    pass


def get_user_by_nickname(nickname):
    query = db.session.query(WpUser)
    query = query.options(load_only('ID', 'user_pass'))
    user = query.first()
    return user


def get_superadmin_user():
    query = db.session.query(WpSiteMeta)
    query = query.options(load_only('meta_value'))
    result = query.first()
    users = loads(result['meta_value'], array_hook=OrderedDict)
    return users.values()


def remove_capabilities_and_userlevel(user_id):
    capabilities = '%' + '_capabilities'
    user_level = '%' + '_user_level'

    db.session.query(WpUserMeta)\
        .filter(WpUserMeta.meta_key.like(capabilities))\
        .filter(WpUserMeta.user_id == user_id)\
        .delete()

    db.session.query(WpUserMeta)\
        .filter(WpUserMeta.meta_key.like(user_level))\
        .filter(WpUserMeta.user_id == user_id)\
        .delete()

    db.session.commit()


def normalize(row, keys):
    for key in row.keys():
        keys[key] = row[key]
    return keys


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))


@login_manager.user_loader
def user_loader(nickname):
    user = User()
    user.id = nickname
    return user


@login_manager.request_loader
def request_loader(request):
    nickname = request.form.get('nickname')
    superadmin_users = get_superadmin_user()
    if nickname in superadmin_users:
        user = User()
        user.id = nickname
        user = get_user_by_nickname(nickname)
        success = phasher.check_password(request.form['pw'], user['user_pass'])
        if success:
            user.is_authenticated = success
    return


@app.route('/')
@login_required
def desa():
    return render_template('desa.html', active='desa')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        superadmin_users = get_superadmin_user()
        if nickname in superadmin_users:
            user = get_user_by_nickname(nickname)
            success = phasher.check_password(request.form['pw'], user['user_pass'])
            if success:
                user = User()
                user.id = nickname
                login_user(user)
                return redirect('/')
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/contents')
@login_required
def contents():
    return render_template('contents.html', active='contents', now=datetime.datetime.now())


@app.route('/contents/v2')
@login_required
def contents_v2():
    return render_template('contents_v2.html', active='contents_v2', now=datetime.datetime.now())


@app.route('/code_finder')
@login_required
def code_finder():
    return render_template('code_finder.html', active='code_finder')


@app.route('/user_supradesa')
@login_required
def user_supradesa():
    return render_template('user_supradesa.html', active='user_supradesa')


@app.route('/supradesa')
@login_required
def agregate():
    return render_template('supradesa.html', active='supradesa')


@app.route('/contents/<int:id>')
@login_required
def get_content(id):
    query = db.session.query(SdContent)
    query = query.options(load_only('desa_id', 'subtype', 'type', 'content'))
    query = query.filter(SdContent.id == id)
    content = query.first()
    schema_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../common/schemas/" + content.type + ".json")
    with open(schema_file, 'r') as myfile:
        schema = myfile.read()
    return render_template('content.html', active='contents', content=content, schema=schema)


@app.route('/contents/v2/<int:id>/<type>')
@login_required
def get_content_v2(id, type='data'):
    sheet = request.args.get("sheet", "0")
    query = db.session.query(SdContent)
    query = query.options(load_only('desa_id', 'subtype', 'type', 'content', 'change_id'))
    query = query.filter(SdContent.id == id).filter(SdContent.api_version == '2.0')
    content = query.first()
    schema = []
    keys = []
    json_content = json.loads(content.content);

    if sheet == "null":
        sheet = content.type

    if isinstance(json_content[type], dict):
        for key, value in json_content[type].items():
            keys.append(key)

    if sheet == 'penduduk':
        sheet = 'penduduk_v2'
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../common/schemas/" + sheet + ".json"),'r') as myFile:
            schema = myFile.read()

    return render_template('content_v2.html', active='contents_v2', schema=schema, keys=keys, content=content)


@app.route('/statics/<path:path>')
def send_statics(path):
    return send_from_directory('statics', path)


@app.route('/api/desa', methods=["GET"])
@login_required
def get_desas():
    query = db.session.query(SdDesa)
    desas = query.all()
    return jsonify(desa)


@app.route('/api/desa', methods=["POST"])
@login_required
def update_desa():
    blog_id = int(request.form.get('blog_id'))
    column = str(request.form.get('column'))
    value = str(request.form.get('value'))
    allowed_columns = ["kode", "latitude", "longitude", "sekdes", "kades", "pendamping", "is_dbt", "is_lokpri"]
    boolean_columns = ["is_dbt", "is_lokpri"]

    if column not in allowed_columns:
        return
    if column in ["latitude", "longitude"]:
        value = float(value)
    if column in boolean_columns:
        value = int(value)

    query = db.session.query(SdDesa)\
        .update(dict(column=value))\
        .query.where(SdDesa.blog_id == blog_id)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/desa/update_from_code', methods=["POST"])
@login_required
def update_desa_from_code():
    desa_alias = aliased(SdAllDesa)
    kecamatan_alias = aliased(SdAllDesa)
    kabupaten_alias = aliased(SdAllDesa)
    propinsi_alias = aliased(SdAllDesa)

    db.session.query(SdDesa)\
        .join(desa_alias, SdDesa.kode == desa_alias.region_code)\
        .join(kecamatan_alias, desa_alias.parent_code == kecamatan_alias.region_code)\
        .join(kabupaten_alias, kecamatan_alias.parent_code == kabupaten_alias.region_code)\
        .join(propinsi_alias, kabupaten_alias.parent_code == propinsi_alias.region_code)\
        .update().values(
            desa=desa_alias.region_name,
            kecamatan=kecamatan_alias.region_name,
            kabupaten=kabupaten_alias.region_name,
            propinsi=propinsi_alias.region_name
        )\
        .where(func.trim(func.coalesce(SdDesa.kode, '')) != '')

    db.session.commit()
    return jsonify({'success': True})


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
            address = (desa['desa'] + ', ' + desa['kecamatan'] + ", " + desa['kabupaten']).replace(' ', '+')
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


@app.route('/api/contents/v2', methods=["GET"])
@login_required
def get_contents_v2():
    cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    try:
        filter_value = request.args.get("desa_id", "true")
        filter_text = "'true' = %s"
        if filter_value != "true":
            filter_text = "desa_id = %s"
            filter_value = int(filter_value)
        query = "SELECT sd_contents.id, sd_contents.content, desa_id, d.desa, type, subtype, timestamp, date_created, created_by, u.user_login, opendata_date_pushed, opendata_push_error, change_id, api_version from sd_contents left join sd_desa d on desa_id = d.blog_id left join wp_users u on u.ID = created_by WHERE api_version='2.0' and " + filter_text + " order by date_created desc limit 100"
        cur.execute(query, (filter_value,))
        contents = list(cur.fetchall())
        for c in contents:
            j = json.loads(c["content"])
            if "data" in j and "keys" in dir(j["data"]):
                keys = j["data"].keys()
                for i, key in enumerate(keys):
                    c["d" + str(i)] = len(j["data"][key])
            if "diffs" in j:
                added = 0
                modified = 0
                deleted = 0
                for l in j["diffs"].values():
                    for d in l:
                        added += len(d["added"])
                        modified += len(d["modified"])
                        deleted += len(d["deleted"])
                c["added"] = added
                c["modified"] = modified
                c["deleted"] = deleted
            del c["content"]
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


@app.route('/api/update_users_supradesa', methods=["POST"])
@login_required
def update_user_supradesa():
    data = json.loads(request.form.get("data"))
    cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    keys = {'username': None, 'supradesa_id': None, 'level': None}
    try:
        for values in data:
            print values
            row = normalize(values, keys)
            if row["username"] == None or row["supradesa_id"] == None:
                continue

            query = "SELECT ID FROM wp_users WHERE user_login = %s"
            cur.execute(query, (row["username"],))
            user = cur.fetchone()
            if user == None:
                continue

            query = "SELECT * FROM sd_users_supradesa WHERE username = %s and supradesa_id = %s"
            cur.execute(query, (row["username"], row["supradesa_id"],))
            same = cur.fetchone()
            if same != None:
                continue

            query = "SELECT region_code FROM sd_supradesa WHERE id = %s"
            cur.execute(query, (row["supradesa_id"],))
            code = cur.fetchone()
            if code == None:
                continue

            query = "REPLACE INTO sd_users_supradesa (username, supradesa_id,level) VALUES (%s,%s,%s)"
            cur.execute(query, (row["username"], row["supradesa_id"], row["level"]))
            mysql.connection.commit()
            remove_capabilities_and_userlevel(user["ID"], )

            query = "SELECT blog_id FROM sd_desa WHERE kode like %s"
            cur.execute(query, (code["region_code"] + '.%',), )
            blogs_id = list(cur.fetchall())
            for blog_id in blogs_id:
                role = {"administrator": "10", "editor": "7", "author": "2", "contributor": "1", "subscriber": "0"}
                capabilities = ('wp_' + str(blog_id["blog_id"]) + '_capabilities')
                user_level = ('wp_' + str(blog_id["blog_id"]) + '_user_level')
                level_value = role[row["level"]]
                role = dumps({row["level"]: 1})

                query = """INSERT INTO wp_usermeta (user_id, meta_key,meta_value) VALUES (%s, %s,%s), (%s, %s,%s)"""
                cur.execute(query, (user["ID"], capabilities, role, user["ID"], user_level, level_value))
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

        query = "DELETE FROM sd_users_supradesa WHERE username = %s and supradesa_id = %s"
        cur.execute(query, (data["username"], data["supradesa_id"],))
        mysql.connection.commit()

        query = "SELECT ID from wp_users WHERE user_login = %s"
        cur.execute(query, (data["username"],))
        user = cur.fetchone()
        remove_capabilities_and_userlevel(user["ID"])

        return jsonify({'success': True})
    finally:
        cur.close


@app.route('/api/get_region', methods=["GET"])
@login_required
def get_region():
    cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    try:
        query = "SELECT region_code, id as supradesa_id FROM sd_supradesa"
        cur.execute(query)
        result = jsonify(cur.fetchall())
        return result
    finally:
        cur.close()


@app.route('/api/supradesa', methods=["GET"])
@login_required
def get_supradesa():
    cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    try:
        query = "SELECT * FROM sd_supradesa"
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
    keys = {'id': None, 'region_code': None, 'flag': None, 'name': None, 'blog_agregate': None, 'username': None,
            'password': None, 'zoom': None, 'latitude': None, 'longitude': None}
    try:
        for row in data:
            if row == {}:
                continue
            result = normalize(row, keys)
            query = "REPLACE INTO sd_supradesa (id,region_code,flag,name,blog_agregate,username,password,zoom,latitude,longitude) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(query, (
                result["id"], result["region_code"], result["flag"], result["name"], result["blog_agregate"],
                result["username"], result["password"], result["zoom"], result["latitude"], result["longitude"]))
            mysql.connection.commit()
        return jsonify({'success': True})
    finally:
        cur.close()


@app.route('/api/remove_supradesa', methods=["POST"])
@login_required
def remove_supradesa():
    data = json.loads(request.form.get("data"))
    cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    try:
        query = "SELECT u.ID FROM sd_users_supradesa us INNER JOIN wp_users u ON u.user_login = us.username WHERE us.supradesa_id = %s"
        cur.execute(query, (data["id"],))
        user = cur.fetchone()
        if user != None:
            print "user ada"
            remove_capabilities_and_userlevel(user["ID"])
            query = "DELETE FROM sd_users_supradesa WHERE supradesa_id = %s"
            cur.execute(query, (data["id"],))
            mysql.connection.commit()

        query = "DELETE FROM sd_supradesa WHERE id= %s"
        cur.execute(query, (data["id"],))
        mysql.connection.commit()
        return jsonify({'success': True})
    finally:
        cur.close


if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["ADMIN_PORT"])
