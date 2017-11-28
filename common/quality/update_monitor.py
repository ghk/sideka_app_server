import sys

import MySQLdb
import os
import json
import time
import datetime
from utils import open_cfg, query_single 

def get_sd_desa_query(cur, supradesa_id):
    if supradesa_id == 0:
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



def get_statistics(cur, supradesa_id):
    def combine(row):
        res = json.loads(row[1])
        res["desa"] = row[2]
        res["latitude"] = row[3]
        res["longitude"] = row[4]
        return res
    query_sd_desa = get_sd_desa_query(cur, supradesa_id)
    query = """SELECT s.blog_id, s.statistics, d.desa, d.latitude, d.longitude FROM sd_statistics s INNER JOIN (SELECT blog_id, max(date) as date FROM sd_statistics GROUP BY blog_id ) 
             st ON s.blog_id = st.blog_id AND s.date = st.date left JOIN sd_desa d ON s.blog_id = d.blog_id where {0}""".format(query_sd_desa)

    cur.execute(query)
    results = [combine(c) for c in cur.fetchall()]
    return results

def get_zoom(cur, supradesa_id):
    results = {}
    query = "select zoom,latitude, longitude from sd_supradesa where id = %s"
    cur.execute(query, (supradesa_id,))
    values = cur.fetchone()
    if values is None:
        return results
    header = [column[0] for column in cur.description]
    results = dict(zip(header, values))
    return results

def get_map_statistics(cur, supradesa_id):
    def get_score(stats, node):
        res = {}
        res["score"] = 0
        if node in stats and "score" in stats[node]:
            res["score"] = stats[node]["score"]
        return res
    
    def combine(row):
        stats = json.loads(row[1])
        res = {}
        for node in ["blog", "penduduk", "keuangan", "pemetaan"]:
            res[node] = get_score(stats, node)
        res["domain"] = stats["domain"]
        res["blog_id"] = stats["blog_id"]
        res["desa"] = row[2]
        res["latitude"] = row[3]
        res["longitude"] = row[4]
        return res
    query_sd_desa = get_sd_desa_query(cur, supradesa_id)
    query = """SELECT s.blog_id, s.statistics, d.desa, d.latitude, d.longitude FROM sd_statistics s INNER JOIN (SELECT blog_id, max(date) as date FROM sd_statistics GROUP BY blog_id ) 
             st ON s.blog_id = st.blog_id AND s.date = st.date left JOIN sd_desa d ON s.blog_id = d.blog_id where {0}""".format(query_sd_desa)

    cur.execute(query)
    results = [combine(c) for c in cur.fetchall()]
    return results



def get_dashboard(cur, supradesa_id):
    def combine(row):
        res = json.loads(row[1])
        res["blog_id"] = row[0]
        return res
    results = {}
    query_sd_desa = get_sd_desa_query(cur, supradesa_id)
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
    results["map_statistics"] = get_map_statistics(cur, supradesa_id)
    results["zoom"] = get_zoom(cur, supradesa_id)

    return results




def get_weekly_domain(cur, supradesa_id):
    query_sd_desa = get_sd_desa_query(cur, supradesa_id)
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
    return results




def get_weekly_panel(cur, supradesa_id):
    query_sd_desa = get_sd_desa_query(cur, supradesa_id)
    results = {}
    weekly_keuangan = []
    weekly_penduduk = []
    weekly_posts = []

    def combine(row):
        res = json.loads(row[1])
        res.update(dict(blog_id=row[0], desa=row[2], kecamatan=row[3],
                        kabupaten=row[4], propinsi=row[5], kode=[row[6]]))
        return res
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

    return results

functions = {}
functions["dashboard"] = get_dashboard
functions["statistics"] = get_statistics
#functions["map_statistics"] = get_map_statistics
functions["weekly_domain"] = get_weekly_domain
functions["weekly_panel"] = get_weekly_panel

if __name__ == "__main__":
    conf = open_cfg('../app.cfg')
    db = MySQLdb.connect(host=conf.MYSQL_HOST,
                 user=conf.MYSQL_USER,
                 passwd=conf.MYSQL_PASSWORD,
                 db=conf.MYSQL_DB)
    cur = db.cursor()
    query = "select id from sd_supradesa"
    cur.execute(query)
    supradesas = list(cur.fetchall())
    supradesas.insert(0, [0])
    for supradesa in supradesas:
        supradesa_id = supradesa[0]

        for typ, function in functions.items():
            _id = "%s_%d" % (typ, supradesa_id)
            print _id
            value = function(cur, supradesa_id)
            content = json.dumps(value)
            cur.execute("REPLACE into sd_monitors (id, type, supradesa_id, content, date_created) VALUES (%s, %s, %s, %s, now())", (_id, typ, supradesa_id, content))
            db.commit()
    db.close()
