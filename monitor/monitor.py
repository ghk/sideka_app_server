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

@cache.memoize(timeout=600)
def get_statistics_by_supradesa(supradesa_id):
    def combine(row):
        res = json.loads(row[1])
        res["desa"] = row[2]
        res["latitude"] = row[3]
        res["longitude"] = row[4]
        return res
    query_sd_desa = get_sd_desa_query(supradesa_id)
    cur = mysql.connection.cursor()
    try:
        query = """SELECT s.blog_id, s.statistics, d.desa, d.latitude, d.longitude FROM sd_statistics s INNER JOIN (SELECT blog_id, max(date) as date FROM sd_statistics GROUP BY blog_id ) 
				 st ON s.blog_id = st.blog_id AND s.date = st.date left JOIN sd_desa d ON s.blog_id = d.blog_id where {0}""".format(query_sd_desa)

        print query
        cur.execute(query)
        results = [combine(c) for c in cur.fetchall()]
        return jsonify(results)
    finally:
        cur.close()

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    supradesa_id = str(request.args.get("supradesa_id"))
    return get_statistics_by_supradesa(supradesa_id)


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    def combine(row):
        res = json.loads(row[1])
        res["blog_id"] = row[0]
        return res
    results = {}
    supradesa_id = str(request.args.get("supradesa_id"))
    query_sd_desa = get_sd_desa_query(supradesa_id)
    cur = mysql.connection.cursor()
    try:
        weekly_desa = []
        weekly_posts = []
        weekly_penduduk = []
        weekly_keuangan = []
        weekly_pemetaan = []
        desa_query = "select count(*) from sd_desa as d inner join wp_blogs b on d.blog_id = b.blog_id where {0} and b.registered < ADDDATE(NOW(), INTERVAL %d WEEK);".format(
            query_sd_desa)
        post_query = "select count(distinct(ps.blog_id)) from sd_post_scores ps left join sd_desa d on d.blog_id = ps.blog_id where {0} and ps.post_date > ADDDATE(NOW(), INTERVAL %d WEEK) and ps.post_date < ADDDATE(NOW(), INTERVAL %d WEEK);".format(
            query_sd_desa)
        stats_query = "select s.blog_id, statistics from sd_statistics s left join sd_desa d on d.blog_id = s.blog_id where {0} and date =  ADDDATE((select max(date) from sd_statistics), INTERVAL %d WEEK);".format(
            query_sd_desa)
        for i in range(5):
            start = 0 - i - 1
            end = 0 - i

            cur.execute(desa_query % (end,))
            weekly_desa.append(cur.fetchone()[0])

            cur.execute(post_query % (start, end))
            weekly_posts.append(cur.fetchone()[0])

            cur.execute(stats_query % (end,))
            stats = [combine(c) for c in cur.fetchall()]
            weekly_penduduk.append(
                len(list(filter(lambda s: "penduduk" in s and s["penduduk"]["score"] > 0.5, stats))))
            weekly_keuangan.append(
                len(list(filter(lambda s: "keuangan" in s and s["keuangan"]["score"] > 0.5, stats))))
            weekly_pemetaan.append(
                len(list(filter(lambda s: "pemetaan" in s and s["pemetaan"]["score"] > 0.3, stats))))

        weekly = {}
        weekly["desa"] = weekly_desa
        weekly["post"] = weekly_posts
        weekly["penduduk"] = weekly_penduduk
        weekly["keuangan"] = weekly_keuangan
        weekly["pemetaan"] = weekly_pemetaan
        results["weekly"] = weekly

        daily = {}
        cur.execute(
            "select unix_timestamp(date(ps.post_date)), count(*) from sd_post_scores ps left join sd_desa d on d.blog_id = ps.blog_id where {0} and ps.post_date is not null GROUP BY date(ps.post_date)".format(query_sd_desa))
        daily["post"] = dict(cur.fetchall())
        cur.execute(
            "select unix_timestamp(date(l.date_accessed)), count(*) from sd_logs l left join sd_desa d on d.blog_id = l.desa_id where {0} and l.date_accessed is not null and l.action = 'save_content' and l.type='penduduk' GROUP BY date(date_accessed)".format(query_sd_desa))
        daily["penduduk"] = dict(cur.fetchall())
        cur.execute(
            "select unix_timestamp(date(l.date_accessed)), count(*) from sd_logs l left join sd_desa d on d.blog_id = l.desa_id where {0} and l.date_accessed is not null and l.action = 'save_content' and l.type in ('perencanaan', 'penganggaran', 'spp', 'penerimaan') GROUP BY date(date_accessed)".format(query_sd_desa))
        daily["keuangan"] = dict(cur.fetchall())
        cur.execute(
            "select unix_timestamp(date(l.date_accessed)), count(*) from sd_logs l left join sd_desa d on d.blog_id = l.desa_id where {0} and l.date_accessed is not null and l.action = 'save_content' and l.type='pemetaan' GROUP BY date(date_accessed)".format(query_sd_desa))
        daily["pemetaan"] = dict(cur.fetchall())

        def get_daily(typ, time):
            if time in daily[typ]:
                return daily[typ][time]
            return 0
        r = {"label": [], "post": [], "penduduk": [], "keuangan": [], "pemetaan": []}
        for i in range(63):
            d = datetime.datetime.today() - datetime.timedelta(days=62 - i)
            d = datetime.datetime(d.year, d.month, d.day)
            t = int(time.mktime(d.timetuple()))
            r["label"].append(t)
            r["post"].append(get_daily("post", t))
            r["penduduk"].append(get_daily("penduduk", t))
            r["keuangan"].append(get_daily("keuangan", t))
            r["pemetaan"].append(get_daily("pemetaan", t))

        results["daily"] = r

        return jsonify(results)
    finally:
        cur.close()


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


@app.route('/api/apbdes_scores', methods=["GET"])
def get_apbdes_scores():
    cur = mysql.connection.cursor()
    supradesa_id = str(request.args.get("supradesa_id"))
    query_sd_desa = get_sd_desa_query(supradesa_id)
    try:
        query = "SELECT a.score from sd_apbdes_scores a left join sd_desa d on d.blog_id = a.blog_id where {0}".format(
            query_sd_desa)
        cur.execute(query)
        results = [json.loads(c[0]) for c in cur.fetchall()]
        return jsonify(results)
    finally:
        cur.close()


@app.route('/api/domain_weekly', methods=["GET"])
def get_domain_weekly():
    supradesa_id = str(request.args.get("supradesa_id"))
    query_sd_desa = get_sd_desa_query(supradesa_id)
    cur = mysql.connection.cursor()
    try:

        desa_query = "select count(*) from sd_desa as d inner join wp_blogs b on d.blog_id = b.blog_id where {0} and d.domain like %s and b.registered < ADDDATE(NOW(), INTERVAL %s WEEK);".format(
            query_sd_desa)
        sideka_domain = []
        desa_domain = []
        results = {}
        for i in range(5):
            end = 0 - i

            domain = '%.sideka.id'
            cur.execute(desa_query, (domain, end))
            sideka_domain.append(cur.fetchone()[0])

            domain = '%.desa.id'
            cur.execute(desa_query, (domain, end))
            desa_domain.append(cur.fetchone()[0])

        results["sideka_domain"] = sideka_domain
        results["desa_domain"] = desa_domain
        return jsonify(results)
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


@app.route('/api/panel_weekly')
def get_weekly_panel():
    supradesa_id = str(request.args.get("supradesa_id"))
    query_sd_desa = get_sd_desa_query(supradesa_id)
    cur = mysql.connection.cursor()
    results = {}
    weekly_keuangan = []
    weekly_penduduk = []
    weekly_posts = []

    def combine(row):
        res = json.loads(row[1])
        res.update(dict(blog_id=row[0], desa=row[2], kecamatan=row[3],
                        kabupaten=row[4], propinsi=row[5], kode=[row[6]]))
        return res
    try:

        post_query = "select distinct d.* from sd_post_scores ps left join sd_desa d on d.blog_id = ps.blog_id where {0} and ps.post_date > ADDDATE(NOW(), INTERVAL -1 WEEK) and ps.post_date < ADDDATE(NOW(), INTERVAL 0 WEEK);".format(
            query_sd_desa)
        stats_query = "select s.blog_id, statistics, d.desa, d.kecamatan, d.kabupaten, d.propinsi,d.kode from sd_statistics s left join sd_desa d on d.blog_id = s.blog_id where {0} and date =  ADDDATE((select max(date) from sd_statistics), INTERVAL 0 WEEK);".format(
            query_sd_desa)

        cur.execute(post_query)
        header = [column[0] for column in cur.description]
        values = cur.fetchall()
        results["post"] = list(dict(zip(header, value)) for value in values)

        cur.execute(stats_query)
        stats = [combine(c) for c in cur.fetchall()]
        results["penduduk"] = list(
            filter(lambda s: "penduduk" in s and s["penduduk"]["score"] > 0.5, stats))
        results["keuangan"] = list(
            filter(lambda s: "keuangan" in s and s["keuangan"]["score"] > 0.5, stats))
        results["pemetaan"] = list(
            filter(lambda s: "pemetaan" in s and s["pemetaan"]["score"] > 0.3, stats))

        return jsonify(results)
    finally:
        cur.close()


if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["MONITOR_PORT"])
