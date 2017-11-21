import sys
sys.path.append('../common')

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from flask_compress import Compress
from flask_caching import Cache
from common.phpass import PasswordHash
import MySQLdb
import os
import json
import time
import datetime

app = Flask(__name__)
Compress(app)
mysql = MySQL(app)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

# MySQL configurations
app.config.from_pyfile('../common/app.cfg')

phasher = PasswordHash(8, True)


def get_sd_desa_query(supradesa_id):
    error_value = ["null", "undefined", None]
    cur = mysql.connection.cursor()
    try:
        if supradesa_id in error_value:
            return "true"

        query = "select * from sd_supradesa where id = %s"
        cur.execute(query, (supradesa_id,))
        values = cur.fetchone()
        if values is None:
            return "true"

        header = [column[0] for column in cur.description]
        results = dict(zip(header, values))

        if results["region_code"] is not None:
            query_sd_desa = "d.kode like '{0}.%%'".format(
                results["region_code"])
        elif results["flag"] is not None and results["region_code"] == None:
            query_sd_desa = "{0} = true".format(results["flag"])
        return query_sd_desa
    finally:
        cur.close()

@cache.memoize(timeout=60)
def get_sd_monitor(typ, supradesa_id):
    error_value = ["null", "undefined", None]
    cur = mysql.connection.cursor()
    try:
        if supradesa_id in error_value:
            supradesa_id = 0
        else:
            supradesa_id = int(supradesa_id)

        query = "select content from sd_monitors where type = %s and supradesa_id = %s"
        cur.execute(query, (typ, supradesa_id))
        result = cur.fetchone()
        if result is None:
            return jsonify(None)

        return jsonify(json.loads(result[0]))
    finally:
        cur.close()


@app.route('/')
@app.route('/home')
def dashboard():
    return render_template('dashboard.html', active='dashboard')


@app.route('/statistics')
def statistics():
    return render_template('statistics.html', active='statistics')


@app.route('/statistic/<int:blog_id>')
def statistic_single(blog_id):
    def comb(row):
        res = json.loads(row[0])
        res["date"] = str(row[1])
        return res
    cur = mysql.connection.cursor()
    try:
        post_query = "select score from sd_post_scores p where p.blog_id = %s ORDER BY p.post_date desc"
        desa_query = "select desa, kecamatan, kabupaten, propinsi, domain from sd_desa d where d.blog_id = %s"

        cur.execute(post_query, (blog_id,))
        content_post_quality = json.dumps(
            [json.loads(c[0]) for c in cur.fetchall()])

        cur.execute(desa_query, (blog_id,))
        values = cur.fetchone()
        header = [column[0] for column in cur.description]
        info = json.dumps(dict(zip(header, values)))

        activity_dict = {}
        post_query = "select unix_timestamp(date(ps.post_date)), count(*) from sd_post_scores ps left join sd_desa d on d.blog_id = ps.blog_id where d.blog_id = %s and ps.post_date is not null GROUP BY date(ps.post_date);"
        cur.execute(post_query, (blog_id,))
        activity_dict["post"] = dict(cur.fetchall())
        penduduk_query = "select unix_timestamp(date(l.date_accessed)), count(*) from sd_logs l left join sd_desa d on d.blog_id = l.desa_id where d.blog_id = %s and l.date_accessed is not null and l.action = 'save_content' and l.type='penduduk' GROUP BY date(date_accessed);"
        cur.execute(penduduk_query, (blog_id,))
        activity_dict["penduduk"] = dict(cur.fetchall())
        keuangan_query = "select unix_timestamp(date(l.date_accessed)), count(*) from sd_logs l left join sd_desa d on d.blog_id = l.desa_id where d.blog_id = %s and l.date_accessed is not null and l.action = 'save_content' and l.type in ('perencanaan', 'penganggaran', 'spp', 'penerimaan') GROUP BY date(date_accessed);"
        cur.execute(keuangan_query, (blog_id,))
        activity_dict["keuangan"] = dict(cur.fetchall())
        pemetaan_query = "select unix_timestamp(date(l.date_accessed)), count(*) from sd_logs l left join sd_desa d on d.blog_id = l.desa_id where d.blog_id = %s and l.date_accessed is not null and l.action = 'save_content' and l.type='pemetaan' GROUP BY date(date_accessed);"
        cur.execute(pemetaan_query, (blog_id,))
        activity_dict["pemetaan"] = dict(cur.fetchall())

        def get_daily_activity(typ, time):
            if time in activity_dict[typ]:
                return activity_dict[typ][time]
            return 0

        score_query = "SELECT unix_timestamp(date(s.date)), s.statistics from sd_statistics s where s.blog_id = %s and s.date > DATE_SUB(NOW(), INTERVAL 60 DAY) ORDER BY s.date asc"
        cur.execute(score_query, (blog_id,))
	score_dict = dict(cur.fetchall())

        def get_daily_score(time):
            if time in score_dict:
                result =  json.loads(score_dict[time])
                result["date"] = time
                return result
            return {"penduduk": {"score": 0}, "keuangan": {"score": 0}, "pemetaan": {"score": 0}, "blog": {"score": 0}, "date": time}

        activities = {"label": [], "post": [], "penduduk": [], "keuangan": [], "pemetaan": []}
	scores = []
        for i in range(63):
            d = datetime.datetime.today() - datetime.timedelta(days=62 - i)
            d = datetime.datetime(d.year, d.month, d.day)
            t = int(time.mktime(d.timetuple()))
            activities["label"].append(t)
            activities["post"].append(get_daily_activity("post", t))
            activities["penduduk"].append(get_daily_activity("penduduk", t))
            activities["keuangan"].append(get_daily_activity("keuangan", t))
            activities["pemetaan"].append(get_daily_activity("pemetaan", t))
            scores.append(get_daily_score(t))

        activity_json = json.dumps(activities)
        score_json = json.dumps(scores)

        return render_template('statistic_single.html', active='statistics', score_json=score_json, content_post_quality=content_post_quality, activity_json=activity_json, info=info)
    finally:
        cur.close()


@app.route('/posts')
def post_scores():
    return render_template('post_scores.html', active='post_scores')


@app.route('/apbdes')
def apbdes_scores():
    return render_template('apbdes_scores.html', active='apbdes_scores')


@app.route('/statics/<path:path>')
def send_statics(path):
    return send_from_directory('statics', path)

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    supradesa_id = str(request.args.get("supradesa_id"))
    return get_sd_monitor('statistics', supradesa_id)


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    supradesa_id = str(request.args.get("supradesa_id"))
    return get_sd_monitor('dashboard', supradesa_id)

@app.route('/api/domain_weekly', methods=["GET"])
def get_domain_weekly():
    supradesa_id = str(request.args.get("supradesa_id"))
    return get_sd_monitor('weekly_domain', supradesa_id)

@app.route('/api/panel_weekly')
def get_weekly_panel():
    supradesa_id = str(request.args.get("supradesa_id"))
    return get_sd_monitor('weekly_panel', supradesa_id)


@app.route('/api/post_scores',  methods=["GET"])
def get_post_scores():
    cur = mysql.connection.cursor()
    page = request.args.get('pagebegin')
    item_per_page = int(request.args.get('itemperpage'))
    supradesa_id = str(request.args.get("supradesa_id"))
    query_sd_desa = get_sd_desa_query(supradesa_id)
    offset = 0
    if not page.isdigit():
        page = 1
    if int(page) > 1:
        offset = (int(page) - 1) * item_per_page
    try:
        query = "SELECT p.score from sd_post_scores p left join sd_desa d on p.blog_id = d.blog_id where {0} ORDER BY post_date desc limit %s, %s".format(
            query_sd_desa)
        cur.execute(query, (offset, item_per_page))
        results = [json.loads(c[0]) for c in cur.fetchall()]
        return jsonify(results)
    finally:
        cur.close()


@app.route('/api/count_post_scores', methods=["GET"])
def get_count_post_scores():
    cur = mysql.connection.cursor()
    supradesa_id = str(request.args.get("supradesa_id"))
    query_sd_desa = get_sd_desa_query(supradesa_id)
    try:
        query = "SELECT count(*) from sd_post_scores p left join sd_desa d on p.blog_id = d.blog_id where {0}".format(
            query_sd_desa)
        cur.execute(query)
        results = cur.fetchone()[0]
        return str(results)
    finally:
        cur.close()



@app.route('/api/supradesa')
def get_supradesa():
    cur = mysql.connection.cursor()
    results = []
    try:
        cur.execute("select id,region_code, flag, name from sd_supradesa")
        header = [column[0] for column in cur.description]
        for values in cur.fetchall():
            results.append(dict(zip(header, values)))
        return jsonify(results)
    finally:
        cur.close()


@app.route('/api/get_zoom', methods=["GET"])
def get_zoom():
    cur = mysql.connection.cursor()
    supradesa_id = str(request.args.get("supradesa_id"))
    results = {}
    try:
        query = "select zoom,latitude, longitude from sd_supradesa where id = %s"
        cur.execute(query, (supradesa_id,))
        values = cur.fetchone()
        if values is None:
            return jsonify(results)
        header = [column[0] for column in cur.description]
        results = dict(zip(header, values))
        return jsonify(results)
    finally:
        cur.close()




if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["MONITOR_PORT"])
