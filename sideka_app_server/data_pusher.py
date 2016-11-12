import MySQLdb
import itertools
import csv
import os
import types
from datetime import date
from ckanapi import RemoteCKAN
from penduduk_pusher import PendudukPusher

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
	WHERE c.is_data_synchronized is null order by timestamp asc
""")

contents = list(cur.fetchall())

print len(contents)

for content in contents:
	domain = content["domain"]
	desa_slug = domain.split(".")[0]
	print desa_slug
	print "%d %s: %s %s %d" % (content["desa_id"], content["desa"], content["type"], content["subtype"], content["timestamp"])
	penduduk_pusher = PendudukPusher(desa_slug, ckan, content["content"])
	print penduduk_pusher


db.close()
