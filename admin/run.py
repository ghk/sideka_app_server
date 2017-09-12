import sys

sys.path.append("../common");

from admin import app, db, login_manager
from flask import request, jsonify, render_template, send_from_directory, redirect, url_for
from flask_login import login_user, login_required, logout_user, UserMixin
from sqlalchemy.orm import load_only, aliased
from sqlalchemy import func, desc, update

from phpserialize import *
from collections import OrderedDict
from common import PasswordHash, gzipped
from models import *

import os
import json
import urllib
import datetime

phasher = PasswordHash(8, True)


class User(UserMixin):
    pass


def get_user_by_nickname(nickname):
    user = db.session.query(WpUser)\
        .filter(WpUser.user_login == nickname)\
        .first()
    return user


def get_superadmin_user():
    site_meta = db.session.query(WpSiteMeta)\
        .filter(WpSiteMeta.meta_key == 'site_admins')\
        .first()

    if site_meta is not None:
        users = loads(site_meta.meta_value, array_hook=OrderedDict)

    return users.values()


def remove_capabilities_and_userlevel(user_id):
    capabilities = '%' + '_capabilities'
    user_level = '%' + '_user_level'

    db.session.query(WpUserMeta) \
        .filter(WpUserMeta.meta_key.like(capabilities)) \
        .filter(WpUserMeta.user_id == user_id) \
        .delete()

    db.session.query(WpUserMeta) \
        .filter(WpUserMeta.meta_key.like(user_level)) \
        .filter(WpUserMeta.user_id == user_id) \
        .delete()


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
        success = phasher.check_password(request.form['pw'], user.user_pass)
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
            if user is None:
                success = False
            else:
                success = phasher.check_password(request.form['pw'], user.user_pass)
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
    schema_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "../common/schemas/" + content.type + ".json")
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
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../common/schemas/" + sheet + ".json"),
                  'r') as myFile:
            schema = myFile.read()

    return render_template('content_v2.html', active='contents_v2', schema=schema, keys=keys, content=content)


@app.route('/statics/<path:path>')
def send_statics(path):
    return send_from_directory('statics', path)


@app.route('/api/desas', methods=["GET"])
@login_required
def get_desas():
    desas = db.session.query(SdDesa).all()
    result = SdDesaSchema(many=True).dump(desas)
    return jsonify(result.data)


@app.route('/api/desas/<int:blog_id>', methods=["POST"])
@login_required
def update_desa(blog_id):
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

    update_value = { column: value }
    query = db.session.query(SdDesa) \
        .filter(SdDesa.blog_id == blog_id) \
        .update(update_value) \

    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/desas/update_from_code', methods=["POST"])
@login_required
def update_desa_from_code():
    desa_alias = aliased(SdAllDesa)
    kecamatan_alias = aliased(SdAllDesa)
    kabupaten_alias = aliased(SdAllDesa)
    propinsi_alias = aliased(SdAllDesa)

    query = update(SdDesa).values(
        desa=desa_alias.region_name,
        kecamatan=kecamatan_alias.region_name,
        kabupaten=kabupaten_alias.region_name,
        propinsi=propinsi_alias.region_name
    )
    query = query.where(SdDesa.kode == desa_alias.region_code)
    query = query.where(desa_alias.parent_code == kecamatan_alias.region_code)
    query = query.where(kecamatan_alias.parent_code == kabupaten_alias.region_code)
    query = query.where(kabupaten_alias.parent_code == propinsi_alias.region_code)
    query = query.where(func.trim(func.coalesce(SdDesa.kode, '')) != '')

    db.session.execute(query)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/desas', methods=["POST"])
@login_required
def update_sd_desa():
    max_blog_id = db.session.query(func.max(SdDesa.blog_id)).first()
    wp_blogs_query = db.session.query(WpBlog) \
        .options(load_only('blog_id', 'domain')) \

    if max_blog_id[0] is not None:
        wp_blogs_query = wp_blogs_query.filter(WpBlog.blog_id > max_blog_id[0])

    wp_blogs = wp_blogs_query.all()

    sd_desas = []
    for wp_blog in wp_blogs:
        sd_desa = SdDesa()
        sd_desa.blog_id = wp_blog.blog_id
        sd_desa.domain = wp_blog.domain
        sd_desas.append(sd_desa)
        db.session.add_all(sd_desas)
        db.session.flush()

    query = update(SdDesa).values(domain=WpBlog.domain).where(SdDesa.blog_id == WpBlog.blog_id)
    db.session.execute(query)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/desas/empty_latlong', methods=["POST"])
@login_required
def desa_empty_latlong():
    query = db.session.query(SdDesa) \
        .options(load_only('blog_id', 'desa', 'kecamatan', 'kabupaten')) \
        .filter(SdDesa.latitude == None) \
        .filter(SdDesa.longitude == None) \
        .filter(SdDesa.kode <> None) \
        .filter(SdDesa.kode <> '')

    desas = query.all()
    results = []

    for desa in desas:
        address = (desa.desa + ', ' + desa.kecamatan + ", " + desa.kabupaten).replace(' ', '+')
        url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=AIzaSyATCm-ki0JV9hjtjQXOKvqwlMaBWpYByEc" % address
        results.append(url)
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        if data["status"] == "OK":
            result = data["results"][0]
            latitude = result["geometry"]["location"]["lat"]
            longitude = result["geometry"]["location"]["lng"]
            desa.latitude = latitude
            desa.longitude = longitude
            db.session.add(desa)
        else:
            results.append("%s: not found" % (address,))

    db.session.commit()
    return jsonify(results)


@app.route('/api/contents', methods=["GET"])
@login_required
def get_contents():
    sd_desa_alias = aliased(SdDesa)
    wp_user_alias = aliased(WpUser)
    query = db.session.query(SdContent.id, SdContent.desa_id, sd_desa_alias.desa,
                             SdContent.type, SdContent.subtype, SdContent.timestamp,
                             SdContent.date_created, SdContent.created_by, wp_user_alias.user_login,
                             SdContent.opendata_date_pushed, SdContent.opendata_push_error) \
        .join(sd_desa_alias, SdContent.desa_id == sd_desa_alias.blog_id) \
        .join(wp_user_alias, SdContent.created_by == wp_user_alias.ID) \
        .order_by(desc(SdContent.date_created)) \
        .limit(1000)

    contents = query.all()
    return jsonify(contents)


@app.route('/api/contents/v2', methods=["GET"])
@login_required
def get_contents_v2():
    sd_desa_alias = aliased(SdDesa)
    wp_user_alias = aliased(WpUser)
    query = db.session.query(SdContent.id, SdContent.content, SdContent.desa_id,
                             sd_desa_alias.desa, sd_desa_alias.domain, SdContent.type,
                             SdContent.subtype, SdContent.timestamp, SdContent.date_created,
                             SdContent.created_by, wp_user_alias.user_login, SdContent.opendata_date_pushed,
                             SdContent.opendata_push_error, SdContent.change_id, SdContent.api_version) \
        .join(sd_desa_alias, SdContent.desa_id == sd_desa_alias.blog_id) \
        .join(wp_user_alias, SdContent.created_by == wp_user_alias.ID) \
        .filter(SdContent.api_version == '2.0')

    desa_id = request.args.get("desa_id", "true")
    if desa_id != "true":
        query = query.filter(SdContent.desa_id == int(desa_id))

    domain = request.args.get("domain", "true")
    if domain != "true":
        filter_value = domain + ".%"
        query = query.filter(sd_desa_alias.domain.like(filter_value))

    type_filter_value = request.args.get("type", "true")
    if type_filter_value != "true":
        query = query.filter(SdContent.type == type_filter_value)

    query = query.order_by(desc(SdContent.date_created))
    query = query.limit(100)

    contents = query.all()
    result = []

    for content in contents:
        c = content._asdict()
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
        result.append(c)

    return jsonify(result)


@app.route('/api/statistics', methods=["GET"])
@login_required
def get_statistics():
    statistics = db.session.query(SdStatistics).all()
    return jsonify(statistics)


@app.route('/api/desas/search', methods=["GET"])
@login_required
def search_all_desa():
    q = str(request.args.get('q')).lower()
    kecamatan_alias = aliased(SdAllDesa)
    kabupaten_alias = aliased(SdAllDesa)
    propinsi_alias = aliased(SdAllDesa)

    query = db.session.query(SdAllDesa.region_code, SdAllDesa.region_name.label('desa'),
                             kecamatan_alias.region_name.label('kecamatan'),
                             kabupaten_alias.region_name.label('kabupaten'),
                             propinsi_alias.region_name.label('propinsi')) \
        .join(kecamatan_alias, SdAllDesa.parent_code == kecamatan_alias.region_code) \
        .join(kabupaten_alias, kecamatan_alias.parent_code == kabupaten_alias.region_code) \
        .join(propinsi_alias, kabupaten_alias.parent_code == propinsi_alias.region_code) \
        .filter(func.lower(SdAllDesa.region_name).like(q)) \
        .filter(SdAllDesa.depth == 4) \
        .limit(100)

    results = query.all()
    return jsonify(results)


@app.route('/api/user_supradesas', methods=["GET"])
@login_required
def get_user_supradesa():
    user_supradesas = db.session.query(SdUserSupradesa).all()
    return jsonify(user_supradesas)


@app.route('/api/user_supradesas', methods=["POST"])
@login_required
def update_user_supradesa():
    data = json.loads(request.form.get("data"))
    keys = {'username': None, 'supradesa_id': None, 'level': None}

    for values in data:
        print values
        row = normalize(values, keys)
        if row["username"] == None or row["supradesa_id"] == None:
            continue

        user = db.session.query(WpUser) \
            .filter(WpUser.user_login == row["username"]) \
            .first()
        if user == None:
            continue

        user_supradesa = db.session.query(SdUserSupradesa) \
            .filter(SdUserSupradesa.username == row["username"]) \
            .filter(SdUserSupradesa.supradesa_id == row["supradesa_id"]) \
            .first()
        if user_supradesa != None:
            continue

        region_code = db.session.query(SdSupradesa.region_code) \
            .filter(SdSupradesa.id == row["supradesa_id"]) \
            .first()
        if region_code == None:
            continue

        user_supradesa = db.session.query(SdUserSupradesa) \
            .filter(SdUserSupradesa.username == row["username"]) \
            .filter(SdUserSupradesa.supradesa_id == row["supradesa_id"]) \
            .first()

        if user_supradesa is None:
            user_supradesa = SdUserSupradesa()
            user_supradesa.username = row["username"]
            user_supradesa.supradesa_id = row["supradesa_id"]
        user_supradesa.level = row["level"]

        db.session.add(user_supradesa)
        db.session.flush()
        remove_capabilities_and_userlevel(user["ID"], )

        blogs_id = db.session.query(SdDesa.blog_id) \
            .filter(SdDesa.kode.like(region_code + '.%')) \
            .all()

        for blog_id in blogs_id:
            role = {"administrator": "10", "editor": "7", "author": "2", "contributor": "1", "subscriber": "0"}
            capabilities = ('wp_' + str(blog_id["blog_id"]) + '_capabilities')
            user_level = ('wp_' + str(blog_id["blog_id"]) + '_user_level')
            level_value = role[row["level"]]
            role = dumps({row["level"]: 1})

            wp_usermeta = WpUserMeta()
            wp_usermeta.user_id = user["ID"]
            wp_usermeta.meta_key = capabilities
            wp_usermeta.meta_value = role

            wp_usermeta2 = WpUserMeta()
            wp_usermeta2.user_id = user["ID"]
            wp_usermeta2.meta_key = user_level
            wp_usermeta2.meta_value = level_value

            db.session.add(wp_usermeta)
            db.session.add(wp_usermeta2)

    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/user_supradesas', methods=["DELETE"])
@login_required
def remove_user_supradesa():
    data = json.loads(request.form.get("data"))

    db.session.query(SdUserSupradesa) \
        .filter(SdUserSupradesa.username == data["username"]) \
        .filter(SdUserSupradesa.supradesa_id == data["supradesa_id"]) \
        .delete()

    wp_user = db.session.query(WpUser) \
        .filter(WpUser.user_login == data["username"]) \
        .first()

    if wp_user is not None:
        remove_capabilities_and_userlevel(wp_user["ID"])

    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/regions', methods=["GET"])
@login_required
def get_regions():
    supradesas = db.session.query(SdSupradesa.region_code, SdSupradesa.id.label('id')).all()
    result = []
    for supradesa in supradesas:
        result.append(supradesa._asdict())

    return jsonify(result)


@app.route('/api/supradesas', methods=["GET"])
@login_required
def get_supradesas():
    supradesas = db.session.query(SdSupradesa).all()
    result = SdSupradesaSchema(many=True).dump(supradesas)
    return jsonify(result.data)


@app.route('/api/supradesas', methods=["POST"])
@login_required
def save_supradesa():
    data = json.loads(request.form.get("data"))
    keys = {'id': None, 'region_code': None, 'flag': None, 'name': None, 'blog_agregate': None, 'username': None,
            'password': None, 'zoom': None, 'latitude': None, 'longitude': None}

    for row in data:
        if row == {}:
            continue

        result = normalize(row, keys)

        supradesa = db.session.query(SdSupradesa) \
            .filter(SdSupradesa.id == result["id"]) \
            .first()

        if supradesa is None:
            supradesa = SdSupradesa()
        supradesa.region_code = result["region_code"]
        supradesa.flag = result["flag"]
        supradesa.name = result["name"]
        supradesa.blog_agregate = result["blog_agregate"]
        supradesa.username = result["username"]
        supradesa.password = result["password"]
        supradesa.zoom = result["zoom"]
        supradesa.latitude = result["latitude"]
        supradesa.longitude = result["longitude"]

        db.session.add(supradesa)

    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/supradesas', methods=["DELETE"])
@login_required
def remove_supradesa():
    data = json.loads(request.form.get("data"))
    user = db.session.query(SdUserSupradesa, WpUser.ID) \
        .join(WpUser, SdUserSupradesa.username == WpUser.user_login) \
        .filter(SdUserSupradesa.supradesa_id == data["id"]) \
        .first()

    if user is not None:
        remove_capabilities_and_userlevel(user.ID)
        db.session.query(SdUserSupradesa) \
            .filter(SdUserSupradesa.supradesa_id == data["id"]) \
            .delete()

    db.session.query(SdSupradesa) \
        .filter(SdSupradesa.id == data["id"]) \
        .delete()

    db.session.commit()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["ADMIN_PORT"])
