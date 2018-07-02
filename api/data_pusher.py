import MySQLdb
import itertools
import csv
import os
import types
import sys
import traceback
from datetime import date
import datetime
from ckanapi import RemoteCKAN
from pushers.penduduk_pusher import PendudukPusher
from pushers.keluarga_pusher import KeluargaPusher
from pushers.apbdes_pusher import ApbdesPusher
from utils import open_cfg

conf = open_cfg('../common/app.cfg')

db = MySQLdb.connect(host=conf.MYSQL_HOST,    
                     user=conf.MYSQL_USER,      
                     passwd=conf.MYSQL_PASSWORD,
                     db=conf.MYSQL_DB)        

#ckan =  RemoteCKAN("http://ckan.neon.microvac:5000", apikey="8306ed32-78f3-4f1a-b7e6-b56f9e4f91e4")     
ckan =  RemoteCKAN(conf.CKAN_HOST, apikey=conf.CKAN_KEY)

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor(MySQLdb.cursors.DictCursor)

# Use all the SQL you like
cur.execute("""
SELECT * FROM sd_contents c 
	left join sd_desa d on d.blog_id = c.desa_id
	WHERE c.type in ('penduduk') and c.api_version = '2.0' and c.opendata_date_pushed is null and c.opendata_push_error is null order by c.change_id asc 
""")

contents = list(cur.fetchall())

print len(contents)

pusher_classes = {}
pusher_classes["penduduk"] = PendudukPusher
#pusher_classes["apbdes"] = ApbdesPusher


for c in contents:

	print "------------------------------------------------------------"
	domain = c["domain"]
	if not domain:
		if c["desa_id"] is not None:
			print "no domain for domain id: %d" % c["desa_id"]
		else:
			print "no domain for id: %d" % c["id"]
		continue
	desa_slug = domain.split(".")[0]
	print "%d - %d %s %s: %s %s %d" % (c["id"], c["desa_id"], c["desa"], desa_slug, c["type"], c["subtype"], c["change_id"])
   
	if not c["type"] in pusher_classes:
		print "no pusher for %s" % c["type"]
		continue
	try:
		pusher = pusher_classes[c["type"]](desa_slug, ckan, c)
		pusher.setup()
		pusher.push()
		cur.execute("update sd_contents set opendata_date_pushed = %s where id = %s", (datetime.datetime.now(), c["id"]))
		db.commit()
	except Exception as e:
		traceback.print_exc()
		err = str(e)
		if len(err) > 200:
		    err = err[:200]
		cur.execute("update sd_contents set opendata_push_error = %s where id = %s", (err, c["id"]))
		db.commit()

db.close()
