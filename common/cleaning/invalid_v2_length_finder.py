import MySQLdb
import json

from utils import open_cfg, query_single

def fix_content(old_content, err_tab, err_column_len, err_row_lens, err_row_lens_count):
    new_content = {}
    new_content["columns"] = old_content["columns"]
    if "changeId" in old_content:
	new_content["changeId"] = old_content["changeId"]
    if "apiVersion" in old_content:
	new_content["apiVersion"] = old_content["apiVersion"]
    if "diffs" in old_content:
	new_content["diffs"] = old_content["diffs"]

    if err_tab == "logSurat":
	print "fixing log surat by deleting log surat"
	new_content["data"] = old_content["data"]
	new_content["data"]["logSurat"] = []
	return new_content

    if err_tab == "penduduk" and len(err_row_lens) == 1 and 30 in err_row_lens and err_column_len == 34:
	print "fixing 34 30 by setting columns to 30"
	new_content["data"] = old_content["data"]
	new_content["columns"]["penduduk"] = [u'id', u'nik', u'nama_penduduk', u'tempat_lahir', u'tanggal_lahir', u'jenis_kelamin', u'pendidikan', u'agama', u'status_kawin', u'pekerjaan', u'pekerjaan_ped', u'kewarganegaraan', u'kompetensi', u'no_telepon', u'email', u'no_kitas', u'no_paspor', u'golongan_darah', u'status_penduduk', u'status_tinggal', u'kontrasepsi', u'difabilitas', u'no_kk', u'nama_ayah', u'nama_ibu', u'hubungan_keluarga', u'nama_dusun', u'rw', u'rt', u'alamat_jalan']
	return new_content

    if err_tab == "penduduk" and len(err_row_lens) == 2 and 29 in err_row_lens and 30 in err_row_lens:
	if err_row_lens_count[29] == err_row_lens_count[30] or err_row_lens_count[29] < 400 :
	    print "fixing 29 30 by deleting 29"
	    new_content["columns"]["penduduk"] = [u'id', u'nik', u'nama_penduduk', u'tempat_lahir', u'tanggal_lahir', u'jenis_kelamin', u'pendidikan', u'agama', u'status_kawin', u'pekerjaan', u'pekerjaan_ped', u'kewarganegaraan', u'kompetensi', u'no_telepon', u'email', u'no_kitas', u'no_paspor', u'golongan_darah', u'status_penduduk', u'status_tinggal', u'kontrasepsi', u'difabilitas', u'no_kk', u'nama_ayah', u'nama_ibu', u'hubungan_keluarga', u'nama_dusun', u'rw', u'rt', u'alamat_jalan']
	    new_content["data"] = old_content["data"]
	    new_content["data"]["penduduk"] = [i for i in old_content["data"]["penduduk"] if len(i) == 30]
	    return new_content

    if err_tab == "penduduk" and len(err_row_lens) == 2 and 34 in err_row_lens and 30 in err_row_lens and err_column_len == 34:
	print "fixing 34 30 by deleting 30"
	new_content["data"] = old_content["data"]
	new_content["data"]["penduduk"] = [i for i in old_content["data"]["penduduk"] if len(i) == 34]
	return new_content

    print "not fixing"
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
    row_count = 0
    for desa in desas:
        cur.execute("select id, content, timestamp, date_created from sd_contents where desa_id=%s and  type = 'penduduk' and api_version='2.0' order by change_id desc limit 1",(desa["blog_id"],))
        sql_row_penduduk = cur.fetchone()
        if sql_row_penduduk is not None:
            content = json.loads(sql_row_penduduk["content"], encoding='ISO-8859-1')
            tabs = content["data"]
	    if isinstance(tabs, list):
		    print "%d - %s %d is list" % (desa["blog_id"], desa["domain"], sql_row_penduduk["id"])
		    continue
	    is_invalid_len = False
	    row_lens = set()
	    row_lens_count = {}
            for tab, data in tabs.items():
		if content["columns"][tab] == "dict": 
		    continue
		if len(content["columns"][tab]) == 0:
		    continue
		columns_len = len(content["columns"][tab])
		for row in data:
		    row_lens.add(len(row))
		    if len(row) not in row_lens_count:
			row_lens_count[len(row)] = 0
		    row_lens_count[len(row)] += 1
		    if len(row) != columns_len:
			if not is_invalid_len:
				row_count += 1
			is_invalid_len = True
		if is_invalid_len:
		    break
	    if is_invalid_len:
		print "%d - %s %s %d %s %d %s" % (desa["blog_id"], desa["domain"], tab, sql_row_penduduk["id"], str(row_lens), columns_len, str(row_lens_count))
		new_content = fix_content(content,tab, columns_len, row_lens, row_lens_count)
                content_str = json.dumps(new_content, encoding='ISO-8859-1')
                cur.execute("update sd_contents set content = %s where id = %s", (content_str, sql_row_penduduk["id"]))
                db.commit()
    print row_count
    db.close()
