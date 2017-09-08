import MySQLdb
import itertools
import csv
import os
import types
import sys
import traceback
import json

def open_cfg(filename):
	filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
	d = types.ModuleType('config')
	d.__file__ = filename
	try:
		with open(filename) as config_file:
			exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
	except IOError as e:
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

	
