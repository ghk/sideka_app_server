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

conf = open_cfg('app.cfg')

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
	WHERE c.opendata_date_pushed is null and c.opendata_push_error is null order by timestamp asc
""")

contents = list(cur.fetchall())

print len(contents)

pusher_classes = {}
pusher_classes["penduduk"] = PendudukPusher
pusher_classes["keluarga"] = KeluargaPusher
pusher_classes["apbdes"] = ApbdesPusher

for c in contents:
	print "------------------------------------------------------------"
	domain = c["domain"]
	if not domain:
		print "no domain %d" % c["desa_id"]
		continue
	desa_slug = domain.split(".")[0]
	print "%d %s %s: %s %s %d" % (c["desa_id"], c["desa"], desa_slug, c["type"], c["subtype"], c["timestamp"])
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
		cur.execute("update sd_contents set opendata_push_error = %s where id = %s", (str(e), c["id"]))
		db.commit()


db.close()
