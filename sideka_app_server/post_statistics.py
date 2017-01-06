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
from utils import open_cfg
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



def get_word_list():
	filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wordlist.txt")
	with open(filename) as f:
		return set(f.read().splitlines())

word_list = get_word_list()

def get_scale(value, maximum):
	if not isinstance(value, (int, long, float)):
		value = 0
	if value > maximum:
		value = maximum
	if value < 0:
		value = 0
	return float(value) / float(maximum)


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
	result["paragraphs"] = 1 if paragraphs == 0 else paragraphs
	result["words"] = len(words)
	result["sentences"] = len(sentences)
	result["url"] = post["guid"]
	result["domain"] = domain
	result["title"] = post["post_title"]
	result["date"] = str(post["post_date_gmt"])
	result["kbbi"] = len(list(w for w in words if w.lower().strip() in word_list))
	result["kbbi_percentage"] = result["kbbi"] / float(result["words"]) if result["words"] != 0 else 0

	result["score_thumbnail"] = get_scale(1 if result["has_thumbnail"] else 0, 1)
	result["score_kbbi"] = result["kbbi_percentage"]
	result["score_paragraphs"] = get_scale(result["paragraphs"], 4)
	result["score_sentences"] = get_scale(result["sentences"], 20)
	result["score"] = 0.3 * result["score_thumbnail"] + 0.25 * result["score_kbbi"] + 0.25 * result["score_paragraphs"] +  0.2 * result["score_sentences"]
	
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
		query = "select ID, post_date_gmt from wp_"+str(desa["blog_id"])+"_posts where post_status = 'publish' and post_type = 'post'"
		cur.execute(query)
		posts = list(cur.fetchall())
		for post in posts:
			try:
				scores = get_post_scores(cur, desa["blog_id"], desa["domain"], post["ID"])
				s = json.dumps(scores)
				print s
				cur.execute("REPLACE into sd_post_scores (blog_id, post_id, post_date, score_value, score) values(%s, %s, %s, %s, %s)", (desa["blog_id"], post["ID"], post["post_date_gmt"], scores["score"], s))
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
