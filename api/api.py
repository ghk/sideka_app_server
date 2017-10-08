import sys
import traceback
sys.path.append('../common')

from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from phpass import PasswordHash

import MySQLdb
import os
import json
import time
import base64
import uuid

import logging, sys
logging.basicConfig(stream=sys.stderr)
sys.stdout = sys.stderr

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
             'user_nicename': user_nicename, 'apiVersion': app.config["API_VERSION"]})
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

        content_query = "SELECT content, change_id, api_version FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s AND change_id >=%s ORDER BY change_id DESC"
        if content_subtype is None:
            content_query = "SELECT content, change_id, api_version FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s AND change_id >=%s ORDER BY change_id DESC"
        cur.execute(content_query, (content_type, content_subtype, desa_id, client_change_id))

        row = cur.fetchone()
        if row is None:
            return jsonify({}), 404

        content = json.loads(row[0])
        change_id = row[1]
        api_version = row[2]

	if api_version == "1.0":
	    content["columns"] = ["nik","nama_penduduk","tempat_lahir","tanggal_lahir","jenis_kelamin","pendidikan","agama","status_kawin","pekerjaan","pekerjaan_ped","kewarganegaraan","kompetensi","no_telepon","email","no_kitas","no_paspor","golongan_darah","status_penduduk","status_tinggal","kontrasepsi","difabilitas","no_kk","nama_ayah","nama_ibu","hubungan_keluarga","nama_dusun","rw","rt","alamat_jalan"]

        return_data = {"success": True, "changeId": change_id, "apiVersion": api_version, "columns": content["columns"] }
        return_data["change_id"] = change_id #TODO: remove this later

        if client_change_id == 0:
            return_data["data"] = content["data"]
        elif change_id == client_change_id:
            return_data["diffs"] = []
        else:
            diffs = get_diffs_newer_than_client(cur, content_type, content_subtype, desa_id, client_change_id, content["columns"])
            return_data["diffs"] = diffs

        return jsonify(return_data)
    finally:
        cur.close()

@app.route('/content/v2/<int:desa_id>/<content_type>', methods=["POST"])
@app.route('/content/v2/<int:desa_id>/<content_type>/<content_subtype>', methods=["POST"])
def post_content_v2(desa_id, content_type, content_subtype=None):
    print "post content %d, %s, %s" % (desa_id, content_type, content_subtype)
    cur = mysql.connection.cursor()
    try:
        user_id = get_auth(desa_id, cur)
        client_change_id = 0
        result = None

        if request.args.get("changeId", 0) is not None:
            client_change_id = int(request.args.get("changeId", "0"))

        if user_id is None:
            return jsonify({}), 403

        #Find max change id
        max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s"
        if content_subtype is None:
            max_change_id_query = "SELECT MAX(change_id) FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s"

        cur.execute(max_change_id_query, (content_type, content_subtype, desa_id))
        max_change_id_row = cur.fetchone()
        if max_change_id_row[0] is None:
            max_change_id = 0
        else:
            max_change_id = int(max_change_id_row[0])
        new_change_id = max_change_id + 1

        new_content = {"changeId": 0, "data": {}, "columns": {}, "diffs": {}, "apiVersion": app.config["API_VERSION"]};

        #Initialize new content to be saved
        for tab, columns in request.json["columns"].items():
            new_content["data"][tab] = []
            new_content["columns"][tab] = columns
            if "diffs" in request.json and tab in request.json["diffs"]:
                new_content["diffs"][tab] = request.json["diffs"][tab]
            else:
                new_content['diffs'][tab] = []


        latest_content_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s order by change_id DESC"
        if content_subtype is None:
            latest_content_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s order by change_id DESC"

        cur.execute(latest_content_query, (content_type, content_subtype, desa_id))
        latest_content_row = cur.fetchone()

        if latest_content_row is None:
            latest_content = {}
            latest_content["data"] = {}
            latest_content["columns"] = request.json["columns"]
        else:
            latest_content = json.loads(latest_content_row[0])
        diffs = get_diffs_newer_than_client(cur, content_type, content_subtype, desa_id, client_change_id, request.json["columns"])
        return_data = {"success": True, "changeId": new_change_id, "diffs": diffs, "columns": request.json["columns"] }
        
        if isinstance(latest_content["data"], list) and content_type == "penduduk":
            #v1 penduduk content
            #todo: merge diffs columns
            new_content["data"]["penduduk"] = merge_diffs(new_content["columns"]["penduduk"], new_content["diffs"]["penduduk"], [])
        else:
            for tab, new_columns in request.json["columns"].items():
                
                #Initialize so the latest content have the same tab with the posted content
                if tab not in latest_content["columns"]:
                    latest_content["columns"][tab]=new_columns
                if tab not in latest_content["data"]:
                    latest_content["data"][tab]=[]
                   
                if "data" in request.json and tab in request.json["data"] and content_type in ["perencanaan", "penganggaran", "penerimaan", "spp"]:
                    #Special case for client who posted data instead of diffs
                    new_content["data"][tab] = request.json["data"][tab]

                    #Add new diffs to show that the content is rewritten
                    new_content["diffs"][tab].append({"added":[], "deleted": [], "modified":[], "rewritten":True})

                elif(len(new_content["diffs"][tab]) > 0):
                    #There's diffs in the posted content for this tab, apply them to latest data
                    latest_columns = latest_content["columns"][tab]
                    
                    transformed_latest_data = transform_data(latest_content['columns'][tab], new_columns, latest_content["data"][tab])
                    merged_data = merge_diffs(new_columns, new_content['diffs'][tab], transformed_latest_data)

                    new_content["data"][tab] = merged_data
                    new_content['columns'][tab] = new_columns
                else:
                    #There's no diffs in the posted content for this tab, use the old data
                    new_content["data"][tab] = latest_content["data"][tab]

        cur.execute("INSERT INTO sd_contents(desa_id, type, subtype, content, date_created, created_by, change_id, api_version) VALUES(%s, %s, %s, %s, now(), %s, %s, %s)", 
            (desa_id, content_type, content_subtype, json.dumps(new_content), user_id, new_change_id, app.config["API_VERSION"]))
        mysql.connection.commit()    
        logs(user_id, desa_id, "", "save_content", content_type, content_subtype)

        return_data['success'] = True
        return_data["change_id"] = return_data["changeId"] #TODO: remove this later
        
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

def get_diffs_newer_than_client(cur, content_type, content_subtype, desa_id, client_change_id, client_columns):
    diffs = {}
    for tab, columns in client_columns.items():
        diffs[tab] = []

    #Find content newer than client
    newer_than_client_contents_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype=%s AND desa_id=%s AND change_id > %s ORDER BY change_id ASC"
    if content_subtype is None:
        newer_than_client_contents_query = "SELECT content FROM sd_contents WHERE type=%s AND subtype is %s AND desa_id=%s AND change_id > %s ORDER BY change_id ASC"
    cur.execute(newer_than_client_contents_query, (content_type, content_subtype, desa_id, client_change_id))
    newer_than_client_content_rows = cur.fetchall()

    #Concatenate diffs for every content newer than client
    for row in newer_than_client_content_rows:
        content = json.loads(row[0])

        if content.has_key("diffs") == False:
            continue

        for tab, value in content["diffs"].items():
            #only append diffs which exists posted tab
            if tab in client_columns:
                diff_tab_columns = content["columns"][tab]
                client_tab_columns = client_columns[tab]
                for diff in content["diffs"][tab]:
                    if diff_tab_columns == client_tab_columns:
                        diffs[tab].append(diff)
                    else:
                        transformed_diff = {}
                        for typ in ["added", "modified", "deleted"]:
                            transformed_diff[typ] = [transform_data(diff_columns, client_tab_columns, d) for d in diff[typ]]
                        diffs[tab].append(transformed_diff)
    return diffs

def transform_data(from_columns, to_columns, data):
    if from_columns == to_columns:
        return data
    
    from_data_dict = [array_to_object(d, from_columns) for d in data]
    return [object_to_array(d, to_columns) for d in from_data_dict]

def array_to_object(arr, columns):
    result = {}
    counter = 0

    for column in columns:
        result[column] = arr[counter]
        counter += 1
    
    return result

def object_to_array(object, columns):
    result = []

    for column in columns:
        result.append(object.get(column))
    
    return result

def merge_diffs(columns, diffs, data):
    id_idx = 'id' if columns == 'dict'else 0
    for diff in diffs:
        for add in diff["added"]:
            data.append(add)
        for modified in diff["modified"]:
            for index, item in enumerate(data):
                if item[id_idx] == modified[id_idx]:
                    data[index] = modified
        for deleted in diff["deleted"]:
            for item in data:
                if item[id_idx] == deleted[id_idx]:
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

if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["APP_PORT"])
