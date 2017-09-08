import MySQLdb
import itertools
import csv
import os
import types
import sys
import traceback
import json
import pprint
from datetime import datetime, timedelta

from HTMLParser import HTMLParser, HTMLParseError
from htmlentitydefs import name2codepoint
import re

from utils import open_cfg, query_single
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
pp = pprint.PrettyPrinter(indent=4)

def intTryParse(value):
    try:
        return int(value)
    except Exception:
        return None

def calculateSums(rows):
    sums = {}
    def getValue(row, index, rows):
	anggaran = row[2]
	if(anggaran is not None):
	    if(row[0]):
		sums[row[0]] = anggaran
	    return anggaran

	sum = 0
	dotCount = len(row[0].split("."))
	i = index + 1
	allowDetail = True
	#print row
	#print '----'
	while (i < len(rows)):
	    nextRow  = rows[i];
	    #print nextRow
	    nextDotCount = len(nextRow[0].split(".")) if nextRow[0] else 0
	    if(not nextRow[0] and allowDetail):
		nextAnggaran = nextRow[2]
		if(nextAnggaran is not None):
		    sum += nextAnggaran
		    print sum
	    elif(nextRow[0] and nextRow[0].startswith(row[0]) and (dotCount + 1 == nextDotCount)):
		allowDetail = False
		sum += getValue(nextRow, i, rows)
		print "getvalue: %d" % sum
	    elif(nextRow[0] and not nextRow[0].startswith(row[0]) ):
		print "%s, %s, %s" % (row[0], nextRow[0], nextRow[0].startswith(row[0]))
		break
	    i += 1
	sums[row[0]] = sum
	print "-"
	return sum;
    for i, row in enumerate(rows):
	if(row[0] and row[0] not in sums):
	    getValue(row, i, rows)
    return sums;

def normalize(apbdes):
	for row in apbdes:
		if len(row) == 0:
			row.append('')
		if len(row) == 1:
			row.append('')
		if len(row) == 2:
			row.append(0)
		if len(row) == 3:
			row.append('')
		if row[0] is None:
			row[0] = ''
		row[0] = row[0].strip()
		row[2] = intTryParse(row[2])
	return apbdes


def get_apbdes_scores(cur, desa_id, domain, subtype):
	result = {}

	cur.execute("select content, timestamp, date_created from sd_contents where desa_id = %s and type = 'apbdes' and subtype = %s order by timestamp desc", (desa_id,subtype)) 
	one =  cur.fetchone()
	result["last_modified"] = str(one["date_created"])
	result["last_modified_str"] = str(datetime.now() - one["date_created"])
	apbdes = json.loads(one["content"], encoding='ISO-8859-1')["data"]
	normalize(apbdes)
	sums = calculateSums(apbdes)
	result["rows"] = len(apbdes)
	pp.pprint(sums)

	result["pendapatan"] = sums.get("1", 0)
	result["belanja"] = sums.get("2", 0)
	result["domain"] = domain
	result["subtype"] = subtype

	
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

	cur.execute("DELETE from sd_apbdes_scores")
	cur.execute(query)

	for desa in desas:
		print desa["blog_id"]
		query = "SELECT distinct(subtype) from sd_contents where desa_id = %s and type = 'apbdes' order by timestamp desc"
		cur.execute(query, (desa["blog_id"],))
		content = list(cur.fetchall())
		subtypes = set(c["subtype"] for c in content if c["subtype"] is not None)
		years = list(set(s[0:4] for s in subtypes if len(s) >= 4))
		for i, year in list(enumerate(years)):
			if year+"p" in years:
				years[i] = year+"p"
		for subtype in years:
			try:
				scores = get_apbdes_scores(cur, desa["blog_id"], desa["domain"], subtype)
				s = json.dumps(scores)
				print s
				cur.execute("REPLACE into sd_apbdes_scores (blog_id, subtype, score) values(%s, %s, %s)", (desa["blog_id"], subtype, s))
			except Exception as e:
				traceback.print_exc()
				
		db.commit()
	db.close()

if __name__ == "___main__":
	conf = open_cfg('../commmon/app.cfg')
	db = MySQLdb.connect(host=conf.MYSQL_HOST,    
			     user=conf.MYSQL_USER,      
			     passwd=conf.MYSQL_PASSWORD,
			     db=conf.MYSQL_DB)        
	cur = db.cursor(MySQLdb.cursors.DictCursor)
	#scores = get_post_scores(cur, 5, 55)
	#scores = get_apbdes_scores(cur, 25, "papayan", "2016")
	scores = get_apbdes_scores(cur, 29, "kalimas", "2016")
	print scores
	#db.commit()
	db.close()
