import MySQLdb
import json

from utils import open_cfg, query_single

def fix_content(old_content):
    old_content["columns"]=["nik","nama_penduduk","tempat_lahir","tanggal_lahir","jenis_kelamin","pendidikan","agama","status_kawin","pekerjaan","pekerjaan_ped","kewarganegaraan","kompetensi","no_telepon","email","no_kitas","no_paspor","golongan_darah","status_penduduk","status_tinggal","kontrasepsi","difabilitas","no_kk","nama_ayah","nama_ibu","hubungan_keluarga","nama_dusun","rw","rt","alamat_jalan"]
    return old_content

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
    count = 0
    for desa in desas:
        cur.execute("select id, content, timestamp, date_created from sd_contents where desa_id=%s and  type = 'penduduk' and api_version<>'2.0' order by timestamp desc limit 1",(desa["blog_id"],))
        sql_row_penduduk = cur.fetchone()
        if sql_row_penduduk is not None:
            content = json.loads(sql_row_penduduk["content"], encoding='ISO-8859-1')
            is_no_columns = "columns" not in content
            if is_no_columns:
                print "adding columns %d for desa %s" % (sql_row_penduduk["id"], desa["domain"])
                new_content = fix_content(content)
                content_str = json.dumps(new_content, encoding='ISO-8859-1')
                print sql_row_penduduk["content"]
                print content_str
                cur.execute("update sd_contents set content = %s where id = %s", (content_str, sql_row_penduduk["id"]))
                db.commit()

    print count
    db.close()
