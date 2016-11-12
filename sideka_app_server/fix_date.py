import MySQLdb
import itertools
import csv
import os
import types
import sys
import traceback
import json
from datetime import date
import datetime
from ckanapi import RemoteCKAN
from pushers.penduduk_pusher import PendudukPusher
from pushers.keluarga_pusher import KeluargaPusher

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

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor(MySQLdb.cursors.DictCursor)

# Use all the SQL you like
cur.execute("""
SELECT * FROM sd_contents c 
	left join sd_desa d on d.blog_id = c.desa_id
	WHERE c.type = 'penduduk' and c.date_opendata_pushed is null
""")

contents = list(cur.fetchall())
print len(contents)


i = 0
for c in contents:
	print i
	i += 1
	try:
		content = json.loads(c["content"])
		data = content["data"]
		if len(data) == 0:
			continue
		is_long_date = False
		for r in data:
			print r[3]
			if not r[3]:
				continue
			if len(r[3]) > 10:
				is_long_date = True
				break
		if not is_long_date:
			continue
		for r in data:
			if not r[3]:
				continue
			d = r[3]
			r[3] = d[8:10]+"/"+d[5:7]+"/"+d[0:4]
			print d
			print r[3]
		new_content = json.dumps(content)
		cur.execute("update sd_contents set content = %s where id = %s", (new_content, c["id"]))
		db.commit()
	except:
		traceback.print_exc()


db.close()
