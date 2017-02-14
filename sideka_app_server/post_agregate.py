import MySQLdb
import sys
import itertools
import os, sys
from datetime import date
from utils import open_cfg
from urlparse import urlparse

from wordpress_xmlrpc import Client, WordPressPost,WordPressPage
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods.posts import GetPosts,GetPost, NewPost, EditPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media

reload(sys)  
sys.setdefaultencoding('utf8')


if __name__ == "__main__":
    conf = open_cfg('app.cfg')
    db = MySQLdb.connect(host=conf.MYSQL_HOST,
                        user=conf.MYSQL_USER,
                        passwd =conf.MYSQL_PASSWORD,
                        db=conf.MYSQL_DB)
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    
    query = "SELECT * FROM sd_supradesa WHERE region_code is not null and blog_agregate is not null "
    cur.execute(query)
    blogs_agregate =cur.fetchall()
    for blog in blogs_agregate:
        wp = Client('http://'+str(blog["blog_agregate"])+'/xmlrpc.php',blog["username"],blog["password"])
        region_code = blog["region_code"]+'.%'
        query = "SELECT blog_id FROM sd_desa WHERE kode like %s and desa = 'leu'"
        cur.execute(query,(region_code,))
        blogs = cur.fetchall()
        for blog_id in blogs:
            query ="SELECT * FROM wp_%s_posts WHERE post_type = 'post' and post_status = 'publish'"
            cur.execute(query, (blog_id["blog_id"],))
            posts = cur.fetchall()
            for post in posts:
                print post["post_title"]
                query ="SELECT meta_value as id FROM wp_%s_postmeta WHERE meta_key = '_thumbnail_id' and post_id  = %s"
                cur.execute(query,(blog_id["blog_id"], post["ID"],))
                thumb_id = cur.fetchone()

                query ="SELECT * FROM wp_%s_posts WHERE ID  = %s"
                cur.execute(query,(blog_id["blog_id"],thumb_id["id"],))
                thumb = cur.fetchone()
                url_thumb = urlparse(thumb["guid"])
                image = '/var/www/www.sideka.id'+url_thumb.path
                #image = '\microvac\www.sideka.id.2017-02-05\www.sideka.id'+url_thumb.path
                data = {
                    'name':'picture.jpg',
                    'type': 'image/jpeg'
                }
                with open (image,'rb') as img:
                    data['bits'] = xmlrpc_client.Binary(img.read())

                response = wp.call(media.UploadFile(data))
                attachment_id = response['id']

                wp_post = WordPressPost()
                wp_post.title = post["post_title"]
                wp_post.content = post["post_content"]
                wp_post.date = post["post_date"]
                wp_post.date_modified = post["post_modified"]
                wp_post.post_status = post["post_status"]
                wp_post.comment_status = 'closed'
                wp_post.ping_status = 'closed'
                wp_post.link = post["guid"]
                wp_post.user = post["author"]
                wp_post.link = post["guid"]
                wp_post.thumbnail = attachment_id
                wp_post.custom_fields= [
                    {'key':'blogid','value':blog_id["blog_id"]},
                    {'key':'permalink','value':post["guid"]}
                    ]
                wp_post.terms_names = {
                    'category': ['Kabar Desa'] 
                    }

                try:
                    pass
                    id_wp = wp.call(NewPost(wp_post))
                except Exception as err:
                    print ("error{0}".format(err))
                print ""