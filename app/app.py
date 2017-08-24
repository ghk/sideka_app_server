import sys
sys.path.append('../common')

from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from common.phpass import PasswordHash

import MySQLdb
import os
import json
import time
import base64
import uuid

app = Flask(__name__)
mysql = MySQL(app)
# MySQL configurations
app.config.from_pyfile('../common/app.cfg')

phasher = PasswordHash(8, True)


@app.route('/login', methods=["POST"])
def login():
    login = request.json
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT ID, user_pass, user_nicename FROM wp_users where user_login = %s or user_email = %s",
                    (login["user"], login["user"]))
        user = cur.fetchone()

        success = False
        token = 0
        desa_id = 0
        desa_name = None
        user_id = None
        user_nicename = None

        if user is None:
            return jsonify({}), 403

        success = phasher.check_password(login["password"], user[1])

        if success == False:
            return jsonify({"success": False, "message": 'Password is not found'}), 401

        user_id = user[0]
        user_nicename = user[2]
        cur.execute("SELECT meta_value FROM wp_usermeta where user_id = %d and meta_key = 'primary_blog'" % user[0])
        primary_blog = cur.fetchone()

        if primary_blog is None:
            return jsonify({"success": False, "message": 'Primary blog is not found'}), 403

        desa_id = int(primary_blog[0])
        cur.execute("SELECT option_value FROM wp_%d_options where option_name = 'blogname'" % desa_id)
        opt = cur.fetchone()

        if opt is not None:
            desa_name = opt[0]

        token = os.urandom(64).encode('hex')
        cur.execute("INSERT INTO sd_tokens VALUES (%s, %s, %s, %s, now())", (token, user[0], desa_id, login["info"]))
        mysql.connection.commit()
        logs(user_id, desa_id, token, "login", None, None)
        return jsonify(
            {'success': success, 'desa_id': desa_id, 'desa_name': desa_name, 'token': token, 'user_id': user_id,
             'user_nicename': user_nicename, 'api_version': app.config["API_VERSION"]})
    except Exception as e:
        print str(e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cur.close()


@app.route('/logout', methods=["GET"])
def logout():
    cur = mysql.connection.cursor()
    try:
        token = request.headers.get('X-Auth-Token', None)
        cur.execute("DELETE FROM sd_tokens where token = %s", (token,))
        mysql.connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        print str(e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cur.close()


@app.route('/check_auth/<int:desa_id>', methods=["GET"])
def check_auth(desa_id):
    cur = mysql.connection.cursor()
    try:
        user_id = get_auth(desa_id, cur)
        return jsonify({'user_id': user_id})
    except Exception as e:
        print str(e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cur.close();


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
    except Exception as e:
        print str(e)
        return jsonify({"success": False, "message": str(e)}), 500
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
        query = "SELECT content from sd_contents where desa_id = %s and timestamp > %s and type = %s and subtype = %s and api_version = '1.0' order by timestamp desc"

        if content_subtype is None:
            query = "SELECT content from sd_contents where desa_id = %s and timestamp > %s and type = %s and subtype is %s and api_version = '1.0' order by timestamp desc"

        cur.execute(query, (desa_id, timestamp, content_type, content_subtype))
        content = cur.fetchone()

        if content is None:
            return jsonify({}), 404

        logs(user_id, desa_id, "", "get_content", content_type, content_subtype)
        result = json.loads(content[0])
        return jsonify(result)
    except Exception as e:
        print str(e)
        return jsonify({"success": False, "message": str(e)}), 500
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

        cur.execute("SELECT COUNT(*) FROM sd_contents WHERE desa_id = %s AND type = %s AND api_version = %s",
                    (desa_id, content_type, api_version))
        total_data_api = int(cur.fetchone()[0])

        if total_data_api > 0:
            return jsonify({"error": "Sideka desktop needs to be updated"}), 500

        if user_id is None:
            return jsonify({'success': False}), 403

        max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s"

        if content_subtype is None:
            max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s"

        cur.execute(max_change_id_query, (content_type, content_subtype, desa_id))
        cur_fetch_max_change_id = cur.fetchone()

        if cur_fetch_max_change_id[0] is None:
            mex_change_id = 0
        else:
            max_change_id = int(cur_fetch_max_change_id[0])

        if content_type == 'subtypes':
            return jsonify({success: False}), 500

        new_change_id = max_change_id + 1
        timestamp = int(request.json["timestamp"])
        server_timestamp = int(time.time() * 1000)
        print "%d - %d = %d" % (timestamp, server_timestamp, timestamp - server_timestamp)

        if timestamp > server_timestamp or timestamp <= 0:
            print "reseting to server timestamp, diff: %d" % (server_timestamp - timestamp)
            timestamp = server_timestamp

        cur.execute(
            "INSERT INTO sd_contents (desa_id, type, subtype, content, timestamp, date_created, created_by, change_id, api_version) VALUES (%s, %s, %s, %s, %s, now(), %s, %s, %s)",
            (desa_id, content_type, content_subtype, request.data, timestamp, user_id, new_change_id, '1.0'))
        mysql.connection.commit()
        logs(user_id, desa_id, "", "save_content", content_type, content_subtype)
        return jsonify({'success': True})
    except Exception as e:
        print str(e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cur.close()


@app.route('/content/v2/<int:desa_id>/<content_type>', methods=["GET"])
@app.route('/content/v2/<int:desa_id>/<content_type>/<content_subtype>', methods=["GET"])
def get_content_v2(desa_id, content_type, content_subtype=None):
    cur = mysql.connection.cursor()
    try:
        user_id = get_auth(desa_id, cur)

        if user_id is None:
            return jsonify({}), 403

        client_change_id = 0

        if request.args.get("change_id", 0) is not None:
            client_change_id = int(request.args.get("changeId", "0"))

        content_query = "SELECT content, change_id, api_version FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s AND change_id >%s ORDER BY change_id DESC"

        if content_subtype is None:
            content_query = "SELECT content, change_id, api_version FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s AND change_id >%s ORDER BY change_id DESC"

        cur.execute(content_query, (content_type, content_subtype, desa_id, client_change_id))
        cursor = cur.fetchone()

        if cursor is None:
            return jsonify({"success": True, "change_id": client_change_id})

        content = json.loads(cursor[0])
        change_id = cursor[1]
        api_version = cursor[2]

        if api_version != app.config["API_VERSION"]:
            new_content = {"changeId": 0, "data": [], "columns": [], "apiVersion": app.config["API_VERSION"]}

            for index, data in enumerate(content["data"]):
                if isinstance(content["data"][index], list):
                    new_content["data"].append(content["data"][index])
                    new_content["data"][index].insert(0, base64.urlsafe_b64encode(uuid.uuid4().bytes).strip("="))

            if content.has_key("columns"):
                new_content["columns"] = content["columns"]

            new_content["changeId"] = change_id + 1
            query_insert = "INSERT INTO sd_contents(desa_id, type, subtype, content, date_created, created_by, change_id, api_version) VALUES(%s, %s, %s, %s, now(), %s, %s, %s)"
            cur.execute(query_insert, (
            desa_id, content_type, content_subtype, json.dumps(new_content), user_id, new_content["changeId"],
            app.config["API_VERSION"]))
            mysql.connection.commit()
            return jsonify(
                {"change_id": new_content["changeId"], "data": new_content["data"], "api_version": api_version})

        return_data = {"change_id": change_id, "api_version": api_version}

        if content.has_key("center"):
            return_data["center"] = content["center"]

        if client_change_id == 0 or content.has_key("diffs") == False:
            return_data["data"] = content["data"]
        elif content.has_key("diffs"):
            return_data["diffs"] = content["diffs"]

        return jsonify(return_data)
    except Exception as e:
        print str(e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cur.close()


@app.route('/content/v2/<int:desa_id>/<content_type>', methods=["POST"])
@app.route('/content/v2/<int:desa_id>/<content_type>/<content_subtype>', methods=["POST"])
def post_content_v2(desa_id, content_type, content_subtype=None):
    cur = mysql.connection.cursor()
    try:
        user_id = get_auth(desa_id, cur)
        client_change_id = 0
        result = None

        if request.args.get("change_id", 0) is not None:
            client_change_id = int(request.args.get("changeId", "0"))

        if user_id is None:
            return jsonify({}), 403

        max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s"

        if content_subtype is None:
            max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s"

        cur.execute(max_change_id_query, (content_type, content_subtype, desa_id))
        cursor_max_change_id = cur.fetchone()

        if cursor_max_change_id[0] is None:
            max_change_id = 0
        else:
            max_change_id = int(cursor_max_change_id[0])

        contents_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s AND change_id > %s ORDER BY change_id ASC"

        if content_subtype is None:
            contents_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s AND change_id > %s ORDER BY change_id ASC"

        cur.execute(contents_query, (content_type, content_subtype, desa_id, client_change_id))
        cursor_contents = cur.fetchall()

        new_content = {"changeId": 0, "data": {}, "columns": {}, "diffs": {}, "apiVersion": app.config["API_VERSION"]};

        diffs = {}

        for key, value in request.json["columns"].items():
            new_content["data"][key] = []
            new_content["columns"][key] = value
            new_content["diffs"][key] = request.json["diffs"][key]
            diffs[key] = []

        if content_type == 'map':
            new_content['center'] = request.json['center']

        if len(cursor_contents) > 0:
            for value in cursor_contents:
                content = json.loads(value[0])

                if content.has_key("diffs") == False:
                    continue

                for key, value in content["diffs"].items():
                    for diff in content["diffs"][key]:
                        diffs[key].append(diff)

        if content_subtype == 'subtypes':
            return jsonify({success: False}), 500

        new_change_id = max_change_id + 1
        current_content_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s AND change_id=%s"

        if content_subtype is None:
            current_content_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s AND change_id=%s"

        cur.execute(current_content_query, (content_type, content_subtype, desa_id, client_change_id))
        cursor_current_content = cur.fetchone()

        if cursor_current_content is None:
            current_content = new_content
        else:
            current_content = json.loads(cursor_current_content[0])

        merge_method = None
        return_data = {"success": True, "change_id": new_change_id, "diffs": diffs}

        if isinstance(current_content["data"], list):
            new_content["data"]["penduduk"] = merge_diffs(new_content["diffs"]["penduduk"], current_content["data"])
        elif isinstance(current_content["data"], dict):
            for key, value in request.json["columns"].items():
                if (len(new_content["diffs"][key]) > 0):
                    merge_method = merge_map_diffs if content_type == 'map' else merge_diffs
                    new_content["data"][key] = merge_method(new_content["diffs"][key], current_content["data"][key])
                else:
                    new_content["data"][key] = current_content["data"][key]

                new_content["data"][key] = current_content["data"][key]

            if content_type == 'map':
                new_content['center'] = current_content['center']

        cur.execute(
            "INSERT INTO sd_contents(desa_id, type, subtype, content, date_created, created_by, change_id, api_version) VALUES(%s, %s, %s, %s, now(), %s, %s, %s)",
            (desa_id, content_type, content_subtype, json.dumps(new_content), user_id, new_change_id,
             app.config["API_VERSION"]))
        mysql.connection.commit()
        logs(user_id, desa_id, "", "save_content", content_type, content_subtype)
        return_data['success'] = True

        if content_type == 'map':
            return_data['center'] = new_content['center']

        return jsonify(return_data)
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


def merge_diffs(diffs, data):
    for diff in diffs:
        for add in diff["added"]:
            data.append(add)
        for modified in diff["modified"]:
            for index, item in enumerate(data):
                if item[0] == modified[0]:
                    data[index] = modified
        for deleted in diff["deleted"]:
            for item in data:
                if item[0] == deleted[0]:
                    data.remove(item)
    return data


def merge_map_diffs(diffs, data):
    for diff in diffs:
        for added in diff["added"]:
            data.append(added)
        for modified in diff["modified"]:
            for index, item in enumerate(data):
                if item["id"] == modified["id"]:
                    data[index] = modified
        for deleted in diff["deleted"]:
            for item in data:
                if item["id"] == deleted["id"]:
                    data.remove(item)
        return data


def get_auth(desa_id, cur):
    token = request.headers.get('X-Auth-Token', None)

    if token is not None:
        cur.execute("SELECT user_id FROM sd_tokens where token = %s and desa_id = %s", (token, desa_id))
        user = cur.fetchone()

        if user is not None:
            return user[0]
    return None


def logs(user_id, desa_id, token, action, content_type, content_subtype):
    if (token == ""):
        token = request.headers.get('X-Auth-Token', None)

        cur = mysql.connection.cursor()
        print content_type
        cur.execute(
            "INSERT INTO sd_logs (user_id, desa_id, date_accessed, token, action, type, subtype) VALUES (%s, %s, now(), %s, %s, %s, %s)",
            (user_id, desa_id, token, action, content_type, content_subtype))
        mysql.connection.commit()
        cur.close();


@app.route('/content-map/v2/<int:desa_id>/<indicator>', methods=['POST'])
def upload_map_indicator(desa_id, indicator):
    try:
        geojson = request.json["data"]
        result = []

        for data in geojson['features']:
            data['id'] = base64.urlsafe_b64encode(uuid.uuid4().bytes).strip("=")
            data['indicator'] = indicator
            data['properties'] = {}
            result.append(data)

        return jsonify({"success": True, "data": result})
    finally:
        print "close"

if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["PORT"])