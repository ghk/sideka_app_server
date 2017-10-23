import MySQLdb
import json

from utils import open_cfg, query_single

if __name__ == "__main__":
    conf = open_cfg('../app.cfg')
    db = MySQLdb.connect(host=conf.MYSQL_HOST,
                 user=conf.MYSQL_USER,
                 passwd=conf.MYSQL_PASSWORD,
                 db=conf.MYSQL_DB)
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    query="select blog_id, domain from sd_desa"
    cur.execute(query)
    desas = list(cur.fetchall())
    for desa in desas:
        cur.execute("select id, content, timestamp, date_created from sd_contents where desa_id=%s and  type = 'penduduk' and api_version<>'2.0' order by timestamp desc limit 1",(desa["blog_id"],))
        sql_row_penduduk = cur.fetchone()
        if sql_row_penduduk is not None:
            data = json.loads(sql_row_penduduk["content"], encoding='ISO-8859-1')["data"]
            if isinstance(data, list):
                print "%d - %s %d" % (desa["blog_id"], desa["domain"], sql_row_penduduk["id"])
    db.close()
