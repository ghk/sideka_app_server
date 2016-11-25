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

from HTMLParser import HTMLParser, HTMLParseError
from htmlentitydefs import name2codepoint
import re

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

class _HTMLToText(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False
	self.paragraphs = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br') and not self.hide_output:
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._buf.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            self._buf.append('\n')
            self.paragraphs += 1
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_data(self, text):
        if text and not self.hide_output:
            self._buf.append(re.sub(r'\s+', ' ', text))

    def handle_entityref(self, name):
        if name in name2codepoint and not self.hide_output:
            c = unichr(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name):
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith('x') else int(name)
            self._buf.append(unichr(n))

    def get_text(self):
	def encode(text):
	    try:
		text = unicode(text, errors='ignore')
		return text
	    except TypeError:
		return text
	ss = [encode(s) for s in self._buf]
        return re.sub(r' +', ' ', ''.join(ss))

def html_to_text(html):
    """
    Given a piece of HTML, return the plain text it contains.
    This handles entities and char refs, but not javascript and stylesheets.
    """
    parser = _HTMLToText()
    try:
        parser.feed(html)
        parser.close()
    except HTMLParseError:
        pass
    return parser


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

def get_word_list():
	filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wordlist.txt")
	with open(filename) as f:
		return set(f.read().splitlines())

word_list = get_word_list()

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

def get_post_scores(cur, desa_id, domain, post_id):
	result = {}

	cur.execute("select * from wp_"+str(desa_id)+"_posts where ID = %s", (post_id,))
	post = cur.fetchone()
	parser = html_to_text(post["post_content"])
	text = parser.get_text()
	paragraphs = parser.paragraphs
	words = list(t for t in text.split() if t.split() != "")
	sentences = list(t for t in re.split(r'[.!?\n]+', text) if t.split() != "")
	print sentences

	cur.execute("select * from wp_"+str(desa_id)+"_postmeta where post_id = %s", (post_id,))
	metas = list(cur.fetchall())

	result["has_thumbnail"] = len(list(m for m in metas if m["meta_key"] == "_thumbnail_id")) > 0
	result["paragraphs"] = paragraphs
	result["words"] = len(words)
	result["sentences"] = len(sentences)
	result["url"] = post["guid"]
	result["domain"] = domain
	result["title"] = post["post_title"]
	result["date"] = str(post["post_date_gmt"])
	result["kbbi"] = len(list(w for w in words if w.lower().strip() in word_list))
	
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
		print desa["blog_id"]
		query = "select ID from wp_"+str(desa["blog_id"])+"_posts where post_status = 'publish' and post_type = 'post'"
		cur.execute(query)
		posts = list(cur.fetchall())
		for post in posts:
			try:
				scores = get_post_scores(cur, desa["blog_id"], desa["domain"], post["ID"])
				s = json.dumps(scores)
				print s
				cur.execute("REPLACE into sd_post_scores (blog_id, post_id, score) values(%s, %s, %s)", (desa["blog_id"], post["ID"], s))
			except Exception as e:
				traceback.print_exc()
				
		db.commit()
	db.close()

if __name__ == "___main__":
	conf = open_cfg('app.cfg')
	db = MySQLdb.connect(host=conf.MYSQL_HOST,    
			     user=conf.MYSQL_USER,      
			     passwd=conf.MYSQL_PASSWORD,
			     db=conf.MYSQL_DB)        
	cur = db.cursor(MySQLdb.cursors.DictCursor)
	#scores = get_post_scores(cur, 5, 55)
	scores = get_post_scores(cur, 6, "bokor", 452)
	print scores
	db.commit()
	db.close()
