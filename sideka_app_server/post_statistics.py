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

from bs4  import BeautifulSoup
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

def check_uper_lower_case(words):
	lower_case = [word for word in words if word.islower()]
	upper_case = [word for word in words if word.isupper()]
	is_upper = [word for word in words if not word.islower() and not word.isupper()]	
	return is_upper, lower_case, upper_case

def get_score_case(x, y, z):
	Max = len(x)
	score = 0
	if len(y) > Max:
		score = 0.02
	if len(z) > Max:
		score = 0.03
	else:
		score = 0.05
	return score

def get_score_title(text):
	percentage = 0.1
	title = list(t for t in text.split() if t.split() != "")
	#print title
	score = 0.0	
	if len(title) >= 4 and len(title) <= 14:
		score = 0.05
	else:
		score = 0.01
	up_case, low_case, is_case = check_uper_lower_case(title)
	score_case = get_score_case(up_case, low_case, is_case)
	return (score + score_case) / percentage


def get_score_sentences(text):	
	score = 0
	sum_words = 0
	percentage = 0.3 #30 %
	sentences = list(t for t in re.split(r'[.!?\n]+', text) if t.split() != "")
	for text in sentences:
		words = list(t for t in text.split() if t.split() != "")
		sum_words +=len(words)
	mean_words = sum_words / len(sentences)
	if 8 <= mean_words <= 11:
		score = 0.3 
	if 12 <= mean_words <= 17:
		score = 0.2
	if  18 <= mean_words <= 25:
		score = 0.1
	if mean_words > 25:
		score =  0.05
	return float(score / percentage)

def score_resolution_caption(captions):
	score = 0
	for caption in captions:
		try:
			image = BeautifulSoup(str(caption),'html.parser')
			width =  int(image.img["width"])
			if 400 <= width <= 800:
				score = 0.05
			else:
				score = 0.02
		except:
			print "error"
			pass
	return score

def get_score_caption(text):
	percentage = 0.15
	try: 
		score = 0
		content = text.replace("[","<").replace("]",">")
		soup = BeautifulSoup(content, 'html.parser')
		result_caption =  soup.find_all('caption')
		if len(result_caption) >= 1:
			score += 0.05			
			if len(result_caption) > 1:
				score += 0.05
			else:
				score += 0.05
			score_caption = score_resolution_caption(result_caption)	
			score += score_caption		
		return score / percentage
	except:
		pass
	

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
	
	result["score_title"] = get_score_title(post["post_title"])	
	result["score_sentences"] = get_score_sentences(text)
	result["score_caption"] = get_score_caption(post["post_content"])

	result["score_thumbnail"] = get_scale(1 if result["has_thumbnail"] else 0, 1)
	result["score_kbbi"] = result["kbbi_percentage"]
	result["score_paragraphs"] = get_scale(result["paragraphs"], 4)
	
	result["score"] = 0.2 * result["score_thumbnail"] + 0.2 * result["score_kbbi"] + 0.2 * result["score_paragraphs"] +  0.15 * result["score_sentences"] + 0.1 * result["score_title"] + 0.15 * result["score_caption"] 
	print "skor akhir =",result["score"]
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
