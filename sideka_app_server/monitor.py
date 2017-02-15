from flask import Flask, request,jsonify, render_template, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from phpass import PasswordHash
import MySQLdb
import os
import json
import time
import datetime


app = Flask(__name__, static_url_path='')
mysql = MySQL(app)

# MySQL configurations
app.config.from_pyfile('app.cfg')

phasher = PasswordHash(8, True)

@app.route('/')
def dashboard():
	return render_template('monitor/dashboard.html', active='dashboard')

@app.route('/statistics')
def statistics():
	return render_template('monitor/statistics.html', active='statistics')

@app.route('/statistic/<int:blog_id>')
def statistic_single(blog_id):
	def comb(row):
		res = json.loads(row[0])
		res["date"] = str(row[1])
		return res
	def to_json(col):
		result={}
		result["desa"] = col[0]
		result["kecamatan"] = col[1]
		result["kabupaten"] = col[2]
		result["propinsi"] = col[3]
		return json.dumps(result)

	cur = mysql.connection.cursor()
	
	try:
		daily_query = "SELECT s.statistics, s.date from sd_statistics s where s.blog_id = %s ORDER BY s.date asc";
		post_query = "select score from sd_post_scores p where p.blog_id = %s ORDER BY p.post_date desc";
		desa_query = "select desa, kecamatan, kabupaten, propinsi from sd_desa d where d.blog_id = %s"

		cur.execute(daily_query, (blog_id,))
		content_daily = json.dumps([comb(c) for c in cur.fetchall()])
		
		cur.execute(post_query, (blog_id,))
		content_post = json.dumps([json.loads(c[0]) for c in cur.fetchall()])

		cur.execute(desa_query, (blog_id,))
		info = to_json(cur.fetchone())
		return render_template('monitor/statistic_single.html', active='statistics', content_daily=content_daily, content_post = content_post, info = info)
	finally:
		cur.close()

@app.route('/posts/')
def post_scores():
	return render_template('monitor/post_scores.html', active='post_scores')

@app.route('/apbdes')
def apbdes_scores():
	return render_template('monitor/apbdes_scores.html', active='apbdes_scores')

@app.route('/maps')
def statistics_maps():
	return render_template('monitor/statistics_maps.html', active='statistics_maps')


@app.route('/statics/<path:path>')
def send_statics(path):
	return send_from_directory('statics', path)


@app.route('/api/statistics')
def get_statistics():
	def combine(row):
		res = json.loads(row[1])
		res["pendamping"] = row[2]
		res["latitude"] = row[3]
		res["longitude"] = row[4]
		return res

	cur = mysql.connection.cursor()
	try:
		query = """SELECT s.blog_id, s.statistics, d.pendamping, d.latitude, d.longitude FROM sd_statistics s 
				 INNER JOIN (SELECT blog_id, max(date) as date FROM sd_statistics GROUP BY blog_id ) 
				 st ON s.blog_id = st.blog_id AND s.date = st.date left JOIN sd_desa d ON s.blog_id = d.blog_id"""

		cur.execute(query)
		results = [combine(c) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()

@app.route('/api/dashboard')
def get_dashboard_data():
	def combine(row):
		res = json.loads(row[1])
		res["blog_id"] = row[0]
		return res
	results = {}
	cur = mysql.connection.cursor()
	try:
		weekly_desa = []
		weekly_posts = []
		weekly_penduduk = []
		weekly_apbdes = []
		desa_query = "select count(*) from sd_desa d inner join wp_blogs b on d.blog_id = b.blog_id where b.registered < ADDDATE(NOW(), INTERVAL %d WEEK);"
		post_query = "select count(distinct(blog_id)) from sd_post_scores where post_date > ADDDATE(NOW(), INTERVAL %d WEEK) and post_date < ADDDATE(NOW(), INTERVAL %d WEEK);";
		stats_query = "select blog_id, statistics from sd_statistics where date =  ADDDATE((select max(date) from sd_statistics), INTERVAL %d WEEK);"
		for i in range(5):
			start =  0 - i - 1
			end = 0 - i 
			
			cur.execute(desa_query % (end,))
			weekly_desa.append(cur.fetchone()[0])

			cur.execute(post_query % (start, end))
			weekly_posts.append(cur.fetchone()[0])

			cur.execute(stats_query % (end,))
			stats = [combine(c) for c in cur.fetchall()]
			weekly_penduduk.append(len(list(filter(lambda s: s["penduduk"]["score"] > 0.6, stats))))
			weekly_apbdes.append(len(list(filter(lambda s: s["apbdes"]["score"] > 0.6, stats))))

		weekly = {}
		weekly["desa"] = weekly_desa
		weekly["post"] = weekly_posts
		weekly["penduduk"] = weekly_penduduk
		weekly["apbdes"] = weekly_apbdes
		results["weekly"] = weekly

		daily = {}
		cur.execute("select unix_timestamp(date(post_date)), count(*) from sd_post_scores where post_date is not null GROUP BY date(post_date)")
		daily["post"] =  dict(cur.fetchall())
		cur.execute("select unix_timestamp(date(date_accessed)), count(*) from sd_logs where date_accessed is not null and action = 'save_content' and type='penduduk' GROUP BY date(date_accessed)")
		daily["penduduk"] =  dict(cur.fetchall())
		cur.execute("select unix_timestamp(date(date_accessed)), count(*) from sd_logs where date_accessed is not null and action = 'save_content' and type='apbdes' GROUP BY date(date_accessed)")
		daily["apbdes"] =  dict(cur.fetchall())
		
		def get_daily(typ, time):
			if time in daily[typ]:
				return daily[typ][time]
			return 0
		r = {"label":[], "post":[], "penduduk":[], "apbdes":[]}
		for i in range(90):
			d = datetime.datetime.today() - datetime.timedelta(days = 89 - i)
			d = datetime.datetime(d.year, d.month, d.day)
			t = int(time.mktime(d.timetuple()))
			r["label"].append(t)
			r["post"].append(get_daily("post", t))
			r["penduduk"].append(get_daily("penduduk", t))
			r["apbdes"].append(get_daily("apbdes", t))
			
			
		results["daily"] = r
			
		return jsonify(results)
	finally:
		cur.close()

@app.route('/api/post_scores',  methods=["GET"])
def get_post_scores():
	cur = mysql.connection.cursor()
	keywords = request.args.get('keywords')
	page = int(request.args.get('pagebegin'))
	item_per_page = int(request.args.get('itemperpage'))
	offset = 0
	if int(page) >1:
		offset = (int(page) - 1) * item_per_page	
	try:
		query = "SELECT score from sd_post_scores ORDER BY post_date desc limit %s, %s"
		cur.execute(query,(offset,item_per_page))
		results = [json.loads(c[0]) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()
		
@app.route('/api/count_post_scores')
def get_count_post_scores():
	cur = mysql.connection.cursor()
	try:
		query = "SELECT count(*) from sd_post_scores"
		cur.execute(query)
		results = cur.fetchone()[0]
		return str(results)
	finally:
		cur.close()

@app.route('/api/apbdes_scores',)
def get_apbdes_scores():
	cur = mysql.connection.cursor()
	try:
		query = "SELECT score from sd_apbdes_scores"
		cur.execute(query)
		results = [json.loads(c[0]) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()

@app.route('/api/apbdes_scores',)
def get_supradesa():
	cur = mysql.connection.cursor()
	try:
		query = "SELECT * from sd_supradesa where region_code is not null"
		cur.execute(query)
		results = [json.loads(c[0]) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()
	
@app.route('/api/panel_desa',)
def get_():
	cur = mysql.connection.cursor()
	try:
		desa_query = "select count(*) from sd_desa d inner join wp_blogs b on d.blog_id = b.blog_id where d.domain like %s and b.registered < ADDDATE(NOW(), INTERVAL %s WEEK);"
		sideka_domain = []
		desa_domain = []
		results = {}
		for i in range(5):
			end = 0 - i 			
			domain = '%.sideka.id'
			cur.execute(desa_query , (domain,end,))
			sideka_domain.append(cur.fetchone()[0])	

			domain = '%.desa.id'
			cur.execute(desa_query , (domain,end,))
			desa_domain.append(cur.fetchone()[0])	
		
		results["sideka_domain"] = sideka_domain
		results["desa_domain"] = desa_domain
		return jsonify(results)
	finally:
		cur.close()

if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["MONITOR_PORT"])
