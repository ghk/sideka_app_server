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

def get_sd_desa_query(args):	
	supradesa_id = str(args.get("supradesa_id"))
	error_value = ["null","undefined",None]
	cur = mysql.connection.cursor()
	try:
		if supradesa_id in error_value:
			return "true"

		query= "select * from sd_supradesa where id = %s"
		cur.execute(query,(supradesa_id,))
		values = cur.fetchone()
		if values is None:
			return "true"
			
		header = [column[0] for column in cur.description]
		results = dict(zip(header,values))
		
		if results["region_code"] is not  None:
			query_sd_desa = "d.kode like '{0}.%%'".format(results["region_code"])
		elif results["flag"] is not None and results["region_code"] == None:
			query_sd_desa = "{0} = true".format(results["flag"])
		return query_sd_desa
	finally:
		cur.close()
		
@app.route('/')
@app.route('/home')
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
		values = cur.fetchone()
		header = [column[0] for column in cur.description]
		info = json.dumps(dict(zip(header,values)))
		return render_template('monitor/statistic_single.html', active='statistics', content_daily=content_daily, content_post = content_post, info = info)
	finally:
		cur.close()

@app.route('/posts')
def post_scores():
	return render_template('monitor/post_scores.html', active='post_scores')

@app.route('/apbdes')
def apbdes_scores():
	return render_template('monitor/apbdes_scores.html', active='apbdes_scores')

@app.route('/statics/<path:path>')
def send_statics(path):
	return send_from_directory('statics', path)


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
	def combine(row):
		res = json.loads(row[1])
		res["pendamping"] = row[2]
		res["latitude"] = row[3]
		res["longitude"] = row[4]
		return res
	query_sd_desa = get_sd_desa_query(request.args)
	cur = mysql.connection.cursor()
	try:
		query = """SELECT s.blog_id, s.statistics, d.pendamping, d.latitude, d.longitude FROM sd_statistics s INNER JOIN (SELECT blog_id, max(date) as date FROM sd_statistics GROUP BY blog_id ) 
				 st ON s.blog_id = st.blog_id AND s.date = st.date left JOIN sd_desa d ON s.blog_id = d.blog_id where {0}""".format(query_sd_desa)

		cur.execute(query)
		results = [combine(c) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
	def combine(row):
		res = json.loads(row[1])
		res["blog_id"] = row[0]
		return res
	results = {}
	query_sd_desa = get_sd_desa_query(request.args)
	cur = mysql.connection.cursor()
	try:
		weekly_desa = []
		weekly_posts = []
		weekly_penduduk = []
		weekly_apbdes = []
		desa_query = "select count(*) from sd_desa as d inner join wp_blogs b on d.blog_id = b.blog_id where {0} and b.registered < ADDDATE(NOW(), INTERVAL %d WEEK);".format(query_sd_desa)
		post_query = "select count(distinct(ps.blog_id)) from sd_post_scores ps left join sd_desa d on d.blog_id = ps.blog_id where {0} and ps.post_date > ADDDATE(NOW(), INTERVAL %d WEEK) and ps.post_date < ADDDATE(NOW(), INTERVAL %d WEEK);".format(query_sd_desa)
		stats_query = "select s.blog_id, statistics from sd_statistics s left join sd_desa d on d.blog_id = s.blog_id where {0} and date =  ADDDATE((select max(date) from sd_statistics), INTERVAL %d WEEK);".format(query_sd_desa)
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
		cur.execute("select unix_timestamp(date(ps.post_date)), count(*) from sd_post_scores ps left join sd_desa d on d.blog_id = ps.blog_id where {0} and ps.post_date is not null GROUP BY date(ps.post_date)".format(query_sd_desa))
		daily["post"] =  dict(cur.fetchall())
		cur.execute("select unix_timestamp(date(l.date_accessed)), count(*) from sd_logs l left join sd_desa d on d.blog_id = l.desa_id where {0} and l.date_accessed is not null and l.action = 'save_content' and l.type='penduduk' GROUP BY date(date_accessed)".format(query_sd_desa))
		daily["penduduk"] =  dict(cur.fetchall())
		cur.execute("select unix_timestamp(date(l.date_accessed)), count(*) from sd_logs l left join sd_desa d on d.blog_id = l.desa_id where {0} and l.date_accessed is not null and l.action = 'save_content' and l.type='apbdes' GROUP BY date(date_accessed)".format(query_sd_desa))
		daily["apbdes"] =  dict(cur.fetchall())
		
		def get_daily(typ, time):
			if time in daily[typ]:
				return daily[typ][time]
			return 0
		r = {"label":[], "post":[], "penduduk":[], "apbdes":[]}
		for i in range(63):
			d = datetime.datetime.today() - datetime.timedelta(days = 62 - i)
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
	page = request.args.get('pagebegin')
	item_per_page = int(request.args.get('itemperpage'))
	query_sd_desa = get_sd_desa_query(request.args)
	offset = 0
	if not page.isdigit():page=1
	if int(page) >1:
		offset = (int(page) - 1) * item_per_page	
	try:
		query = "SELECT p.score from sd_post_scores p left join sd_desa d on p.blog_id = d.blog_id where {0} ORDER BY post_date desc limit %s, %s".format(query_sd_desa)
		cur.execute(query,(offset,item_per_page))
		results = [json.loads(c[0]) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()
		
@app.route('/api/count_post_scores',methods=["GET"])
def get_count_post_scores():
	cur = mysql.connection.cursor()
	query_sd_desa = get_sd_desa_query(request.args)
	try:
		query = "SELECT count(*) from sd_post_scores p left join sd_desa d on p.blog_id = d.blog_id where {0}".format(query_sd_desa)
		cur.execute(query)
		results = cur.fetchone()[0]
		return str(results)
	finally:
		cur.close()

@app.route('/api/apbdes_scores',methods=["GET"])
def get_apbdes_scores():
	cur = mysql.connection.cursor()
	query_sd_desa = get_sd_desa_query(request.args)
	try:
		query = "SELECT a.score from sd_apbdes_scores a left join sd_desa d on d.blog_id = a.blog_id where {0}".format(query_sd_desa)
		cur.execute(query)
		results = [json.loads(c[0]) for c in cur.fetchall()]
		return jsonify(results)
	finally:
		cur.close()
	
@app.route('/api/domain_weekly',methods=["GET"])
def get_domain_weekly():	
	query_sd_desa = get_sd_desa_query(request.args)
	cur = mysql.connection.cursor()
	try:
		
		desa_query = "select count(*) from sd_desa as d inner join wp_blogs b on d.blog_id = b.blog_id where {0} and d.domain like %s and b.registered < ADDDATE(NOW(), INTERVAL %s WEEK);".format(query_sd_desa)
		sideka_domain = []
		desa_domain = []
		results = {}
		for i in range(5):
			end = 0 - i 		

			domain = '%.sideka.id'
			cur.execute(desa_query , (domain,end))
			sideka_domain.append(cur.fetchone()[0])	

			domain = '%.desa.id'
			cur.execute(desa_query , (domain,end))
			desa_domain.append(cur.fetchone()[0])	
		
		
		results["sideka_domain"] = sideka_domain
		results["desa_domain"] = desa_domain
		return jsonify(results)
	finally:
		cur.close()

@app.route('/api/supradesa')
def get_supradesa():	
	cur = mysql.connection.cursor()
	results= []
	try:
		cur.execute("select id,region_code, flag, name from sd_supradesa")
		header = [column[0] for column in cur.description]
		for values in cur.fetchall(): results.append(dict(zip(header, values)))
		return jsonify(results)
	finally:
		cur.close()

@app.route('/api/panel_weekly')
def get_weekly_panel():		
	query_sd_desa = get_sd_desa_query(request.args)
	cur = mysql.connection.cursor()
	results= {}
	weekly_apbdes = []
	weekly_penduduk = []
	weekly_posts = []
	
	def combine(row):
		res = json.loads(row[1])
		res.update(dict(blog_id = row[0],desa=row[2],kecamatan=row[3],kabupaten=row[4],propinsi=row[5]))
		return res
	try:
		
		post_query = "select distinct d.* from sd_post_scores ps left join sd_desa d on d.blog_id = ps.blog_id where {0} and ps.post_date > ADDDATE(NOW(), INTERVAL -1 WEEK) and ps.post_date < ADDDATE(NOW(), INTERVAL 0 WEEK);".format(query_sd_desa)
		stats_query = "select s.blog_id, statistics, d.desa, d.kecamatan, d.kabupaten, d.propinsi from sd_statistics s left join sd_desa d on d.blog_id = s.blog_id where {0} and date =  ADDDATE((select max(date) from sd_statistics), INTERVAL 0 WEEK);".format(query_sd_desa)
		
		cur.execute(post_query)
		header = [column[0] for column in cur.description]
		values = cur.fetchall()
		results["post"] = list(dict(zip(header,value)) for value in values)		

		cur.execute(stats_query)
		stats = [combine(c) for c in cur.fetchall()]
		results["penduduk"] =list(filter(lambda s: s["penduduk"]["score"] > 0.6, stats))
		results["apbdes"]= list(filter(lambda s: s["apbdes"]["score"] > 0.6, stats))
		
		return jsonify(results)
	finally:
		cur.close()

if __name__ == '__main__':
    app.run(debug=True, host=app.config["HOST"], port=app.config["MONITOR_PORT"])
