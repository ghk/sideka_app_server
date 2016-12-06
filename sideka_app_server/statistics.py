import MySQLdb
import itertools
import csv
import os
import types
import sys
import traceback
import json
from datetime import datetime, timedelta
from ckanapi import RemoteCKAN

def open_cfg(filename):
	filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
	d = types.ModuleType('config')
	d.__file__ = filename
	try:
		with open(filename) as config_file:
			exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
	except IOError as e:
		if silent and e.errno in (errno.ENOENT, errno.EISDIR):
			return False
		e.strerror = 'Unable to load configuration file (%s)' % e.strerror
		raise
	return d

def query_single(cur, query, column, var=None):
	if var is None:
		cur.execute(query) 
	else:
		cur.execute(query, var) 
	one =  cur.fetchone()
	return one[column] if one is not None else None

def get_blog_statistics(cur, desa_id):
	print desa_id
	result = {}
	last_post = query_single(cur, "select max(post_date_gmt) as max from wp_%d_posts where post_status = 'publish' and post_type = 'post'" % desa_id, "max")
	if last_post is not None:
		result["last_post"] = str(last_post)
		result["last_post_str"] = str(datetime.now() - last_post)
	maximum = datetime.now() - timedelta(hours = 24)
	query ="select count(*) as count from wp_"+str(desa_id)+"_posts where post_status = 'publish' and post_type = 'post' and post_date_gmt > %s";
	result["count_24h"] = query_single(cur, query,  "count", (maximum,))
	maximum = datetime.now() - timedelta(weeks = 1)
	result["count_1w"] = query_single(cur, query,  "count", (maximum,))
	maximum = datetime.now() - timedelta(days = 30)
	result["count_30d"] = query_single(cur, query,  "count", (maximum,))
	return result

def mean(numbers):
	return float(sum(numbers)) / max(len(numbers), 1)

def quality(row):
	result = 0
	for column in row:
		if column is not None and column != "":
			result += 1
	return result
		

def get_penduduk_statistics(cur, desa_id):
	result = {}
	cur.execute("select content, timestamp, date_created from sd_contents where desa_id = %s and type = 'penduduk' order by timestamp desc", (desa_id,)) 
	one =  cur.fetchone()
	if one is not None:
		result["last_modified"] = str(one["date_created"])
		result["last_modified_str"] = str(datetime.now() - one["date_created"])
		content = json.loads(one["content"], encoding='ISO-8859-1')["data"]
		result["count"] = len(content)
		result["quality"] = mean([quality(row) for row in content])
	return result

def get_apbdes_statistics(cur, desa_id):
	result = {}

	query = "SELECT distinct(subtype) from sd_contents where desa_id = %s and type = 'apbdes' order by timestamp desc"
	cur.execute(query, (desa_id,))
	content = list(cur.fetchall())
	subtypes = set(c["subtype"][0:4] for c in content if c["subtype"] is not None)
	result["count"] = len(subtypes)

	cur.execute("select content, timestamp, date_created from sd_contents where desa_id = %s and type = 'apbdes' order by timestamp desc", (desa_id,)) 
	one =  cur.fetchone()
	if one is not None:
		result["last_modified"] = str(one["date_created"])
		result["last_modified_str"] = str(datetime.now() - one["date_created"])
	return result

def get_statistics(cur, desa_id):
	result = {}
	result["blog"] = get_blog_statistics(cur, desa_id)
	result["penduduk"] = get_penduduk_statistics(cur, desa_id)
	result["apbdes"] = get_apbdes_statistics(cur, desa_id)
	return result


if __name__ == "__main__":
	conf = open_cfg('app.cfg')
	db = MySQLdb.connect(host=conf.MYSQL_HOST,    
			     user=conf.MYSQL_USER,      
			     passwd=conf.MYSQL_PASSWORD,
			     db=conf.MYSQL_DB)        
	cur = db.cursor(MySQLdb.cursors.DictCursor)
	query = "select blog_id, domain from sd_desa"
	cur.execute(query)
	desas = list(cur.fetchall())
	for desa in desas:
		stats = get_statistics(cur, desa["blog_id"])
		stats["blog_id"] = desa["blog_id"]
		stats["domain"] = desa["domain"]
		statistics = json.dumps(stats)
		print "%d - %s" % (desa["blog_id"], desa["domain"])
		print statistics
		cur.execute("REPLACE into sd_statistics (blog_id, statistics) values(%s, %s)", (desa["blog_id"], statistics))
		db.commit()
	db.close()
