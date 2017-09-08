import MySQLdb
import itertools
import csv
import os
import types
import sys
import traceback
import json
from datetime import datetime, timedelta

from utils import open_cfg, query_single

def get_scale(value, maximum):
	if not isinstance(value, (int, long, float)):
		value = 0
	if value > maximum:
		value = maximum
	if value < 0:
		value = 0
	return float(value) / float(maximum)

def get_blog_statistics(cur, desa_id):
	result = {}
	last_post = query_single(cur, "select max(post_date_gmt) as max from wp_%d_posts where post_status = 'publish' and post_type = 'post'" % desa_id, "max")

	result["score_last_modified"] = 0
	if last_post is not None:
		result["last_post"] = str(last_post)
		result["last_post_str"] = str(datetime.now() - last_post)
		result["score_last_modified"] = get_scale(7 - (datetime.now() - last_post).days, 7)

	query ="select count(*) as count from wp_"+str(desa_id)+"_posts where post_status = 'publish' and post_type = 'post' and post_date_gmt > %s";

	maximum = datetime.now() - timedelta(hours = 24)
	result["count_24h"] = query_single(cur, query,  "count", (maximum,))

	maximum = datetime.now() - timedelta(weeks = 1)
	result["count_1w"] = query_single(cur, query,  "count", (maximum,))
	result["score_weekly"] = get_scale(result["count_1w"], 3)

	maximum = datetime.now() - timedelta(days = 30)
	result["count_30d"] = query_single(cur, query,  "count", (maximum,))
	result["score_monthly"] = get_scale(result["count_30d"], 5)

	result["score_frequency"] = 0.3 * result["score_last_modified"]  + 0.4 * result["score_weekly"] + 0.3 * result["score_monthly"]

	maximum = datetime.now() - timedelta(days = 30)
	query ="select avg(score_value) as avg from sd_post_scores where blog_id = %s and post_date > %s";
	result["score_quality"] = query_single(cur, query,  "avg", (desa_id,maximum))
	if result["score_quality"] is None:
		result["score_quality"] = 0

	result["score"] = 0.6 * result["score_quality"]  + 0.4 * result["score_frequency"]

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
	result["score_quantity"] = 0
	result["score_quality"] = 0
	if one is not None:
		result["last_modified"] = str(one["date_created"])
		result["last_modified_str"] = str(datetime.now() - one["date_created"])
		content = json.loads(one["content"], encoding='ISO-8859-1')["data"]
		result["count"] = len(content)
		result["quality"] = mean([quality(row) for row in content])

		#sampe data is zero row
		if result["count"] in [1130, 1131, 1132, 2260]:
			result["count"] = 0
			result["quality"] = 0

		row_len = 29
		result["score_quantity"] = get_scale(result["count"], 1000)
		result["score_quality"] = get_scale(result["quality"], row_len)
		print row_len
	result["score"] = 0.4 * result["score_quality"] + 0.6 * result["score_quantity"]
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
	result["score_last_modified"] = 0
	if one is not None:
		result["last_modified"] = str(one["date_created"])
		result["last_modified_str"] = str(datetime.now() - one["date_created"])
		result["score_last_modified"] = get_scale(90 - (datetime.now() - one["date_created"]).days, 90)

	cur.execute("select blog_id, subtype, score from sd_apbdes_scores where blog_id = %s", (desa_id,))
	apbdeses = cur.fetchall()
	result["score_quantity"] = get_scale(len(apbdeses), 3)

	total_quality = 0.0
	for apbdes in apbdeses:
		score = json.loads(apbdes["score"], encoding='ISO-8859-1')
		s_row = get_scale(score["rows"], 200)
		s_income = 1.0 if score["pendapatan"] is not None and score["pendapatan"] > 300000000 else 0.0
		s_expense = 1.0 if score["belanja"] is not None and score["belanja"] > 300000000 else 0.0
		total_quality += 0.3 * s_row + 0.35 * s_income + 0.35 * s_expense

	result["score_quality"] = total_quality / len(apbdeses) if len(apbdeses) > 0 else 0

	result["score"] = 0.4 * result["score_quantity"] + 0.5 * result["score_quality"] + 0.1 * result["score_last_modified"]

	return result

def get_statistics(cur, desa_id):
	result = {}
	result["blog"] = get_blog_statistics(cur, desa_id)
	result["penduduk"] = get_penduduk_statistics(cur, desa_id)
	result["apbdes"] = get_apbdes_statistics(cur, desa_id)
	return result


if __name__ == "__main__":
	conf = open_cfg('../common/app.cfg')
	db = MySQLdb.connect(host=conf.MYSQL_HOST,
			     user=conf.MYSQL_USER,
			     passwd=conf.MYSQL_PASSWORD,
			     db=conf.MYSQL_DB)
	cur = db.cursor(MySQLdb.cursors.DictCursor)
	query = "select blog_id, domain from sd_desa"
	cur.execute(query)
	desas = list(cur.fetchall())
	for desa in desas:
		try:
			stats = get_statistics(cur, desa["blog_id"])
			stats["blog_id"] = desa["blog_id"]
			stats["domain"] = desa["domain"]
			statistics = json.dumps(stats)
			print "%d - %s" % (desa["blog_id"], desa["domain"])
			print statistics
			cur.execute("REPLACE into sd_statistics (blog_id, statistics, date) VALUES (%s, %s, now())", (desa["blog_id"], statistics))
			db.commit()
		except Exception as e:
			print e
	db.close()
