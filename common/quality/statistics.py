import MySQLdb
import traceback
import json
import math
import sys
from datetime import datetime, timedelta

from utils import open_cfg, query_single 

def get_scale(value, maximum):
	if not isinstance(value, (int, long, float)):
		value = 0
	if value > maximum:
		value = maximum
	if value < 0:
		value = 0
	return float(value) / float(maximum)

#Grading for Villages' News Grading through Blog Statistic
def get_blog_statistics(cur, desa_id):
	result = {}
	last_post = query_single(cur, "select max(post_date_gmt) as max from wp_%d_posts where post_status = 'publish' and post_type = 'post'" % desa_id, "max")

	result["score_last_modified"] = 0 
	if last_post is not None:
		result["last_post"] = str(last_post)
		result["last_post_str"] = str(datetime.now() - last_post)
		result["score_last_modified"] = get_scale(7 - (datetime.now() - last_post).days, 7)

	query ="select count(*) as count from wp_"+str(desa_id)+"_posts where post_status = 'publish' and post_type = 'post' and post_date_gmt > %s";

	maximum = datetime.now() - timedelta(hours = 24)
	result["count_24h"] = query_single(cur, query,  "count", (maximum,))

	maximum = datetime.now() - timedelta(weeks = 1)
	result["count_1w"] = query_single(cur, query,  "count", (maximum,))
	result["score_weekly"] = get_scale(result["count_1w"], 3)

	maximum = datetime.now() - timedelta(days = 30)
	result["count_30d"] = query_single(cur, query,  "count", (maximum,))
	result["score_monthly"] = get_scale(result["count_30d"], 5)

	result["score_frequency"] = 0.3 * result["score_last_modified"]  + 0.4 * result["score_weekly"] + 0.3 * result["score_monthly"]

	maximum = datetime.now() - timedelta(days = 60)
	query ="select avg(score_value) as avg from sd_post_scores where blog_id = %s and post_date > %s";
	result["score_quality"] = query_single(cur, query,  "avg", (desa_id,maximum))
	if result["score_quality"] is None:
		result["score_quality"] = 0

	result["score"] = 0.6 * result["score_quality"]  + 0.4 * result["score_frequency"]

	return result

def mean(numbers):
	return float(sum(numbers)) / max(len(numbers), 1)

def quality(row):
	result = 0
	for column in row:
		if column is not None and column != "":
			result += 1
	return result


def quality_penduduk(row, column_indexes):
	result= 0
	for index, column in enumerate(row):
		if column is not None and column != "" :
			if index in column_indexes:
				result+=0.8
			else:
				result+=1
	return result

	
def get_penduduk_statistics(cur, desa_id):
	result = { 
        "log_surat": {"score": 0.0, "quality": {"score": 0.0, "quality": 0.0}, "quantity": {"count": 0, "score": 0.0}}, 
        "last_modified": {"date": None, "count": None, "score": 0.0}, 
        "penduduk": {"score": 0.0, "quality": {"count": 0.0, "score": 0.0}, "quantity": {"count": 0, "score": 0.0}}, 
        "mutasi": {"score": 0.0, "quality": {"score": 0.0, "quality": 0.0}, "quantity": {"count": 0, "score": 0.0}}, 
        "score_last_modified": 0 , 
        "score" :0.0, 
        "content_id": None
    }
	cur.execute("select id, content, change_id, date_created from sd_contents where desa_id = %s and type = 'penduduk' and api_version='2.0' order by change_id desc", (desa_id,))
	sql_row_penduduk =  cur.fetchone()
	penduduk=result["penduduk"]
	other_layers=["mutasi" , "log_surat"]
	result["score_last_modified"]=0
	result["score"] = 0

	if sql_row_penduduk is not None:
		result["content_id"] = sql_row_penduduk["id"]
		last_modified=result["last_modified"]
		last_modified["date"] = str(sql_row_penduduk["date_created"])
		last_modified["count"] = str(datetime.now() -sql_row_penduduk["date_created"])
		last_modified["score"]= get_scale(7 -(datetime.now() - sql_row_penduduk["date_created"]).days , 7)
		print sql_row_penduduk["id"]
		penduduk_cur = json.loads(sql_row_penduduk["content"], encoding='ISO-8859-1')["data"]

		for layer in other_layers:
			tab = []
			if layer in penduduk_cur:
				tab = penduduk_cur[layer]
			layer_score = result[layer]
			layer_score["score"]=0
			quantity_count = len(tab)
			quantity_score = get_scale(quantity_count, 10)
			layer_score["quantity"] = {"count": quantity_count, "score": quantity_score}
			quality_count= mean([quality(row) for row in tab])
			quality_score = get_scale(quality_count, 6)
			layer_score["quality"]= {"quality" : quality_count , "score" : quality_score}
			layer_score["score"]= 0.2*result["score_last_modified"] + 0.4*layer_score["quantity"]["score"] + 0.4*layer_score["quality"]["score"]
			result[layer]=layer_score
		layer_score_sum=layer_score["score"]/2

		penduduk_uncounted=["pekerjaan_ped" , "kewarganegaraan" , "kompetensi", "no_telepon" , "email", "no_kitas" , "no_paspor" , "golongan_darah" , "status_penduduk" , "status_tinggal" , "kontrasepsi", "difabilitas"]
		penduduk_cur_ = json.loads(sql_row_penduduk["content"], encoding='ISO-8859-1')
		columns = penduduk_cur_["columns"]["penduduk"] ; columns_quantity= penduduk_cur_["data"]["penduduk"]
		column_indexes= [columns.index(i)  for i in penduduk_uncounted if i in columns]
		penduduk ["score"]=0
		count_p=len(columns_quantity)
		quality_p = mean([quality_penduduk(row,column_indexes) for row in columns])
		max_quality= len(penduduk_uncounted) * 0.8 + (len(columns) - len(penduduk_uncounted)) * 1

		if quantity_count in [1130, 1131, 1132, 2260]:
			count_p=0
			quality_p=0

		quantity_score_p=get_scale(count_p, 1000)
		quality_score_p=get_scale(quality_p, max_quality)
		penduduk["quantity"]={"count": count_p, "score":quantity_score_p }
		penduduk["quality"]={"count": quality_p , "score" :quality_score_p}
		penduduk["score"]=0.1*last_modified["score"] + 0.6*penduduk["quantity"]["score"] + 0.3* penduduk["quality"]["score"]
		result["score"]=0.8*penduduk["score"]+0.2*layer_score_sum

	return result


def get_renstra_category_score(renstra, category):
	for row in renstra:
		if row[1] == category:
			return 1.0
	return 0

def get_keuangan_statistics(cur, desa_id):
	result = {
        "score" : 0.0, 
        "spp": {
            "spp_bukti": {"quality": {"count": 0.0, "score": 0.0}, "quantity": {"count": 0, "score": 0.0}}, 
            "spp": {"quality": {"count": 0.0, "score": 0.0}, "quantity": {"count": 0, "score": 0.0}}, 
            "date": {"max": None, "count": None, "score": 0.0}, 
            "score": 0.0, 
            "content_id": None,
            "last_modified": {"date": None, "count": None , "score": 0.0}, 
            "spp_rinci": {"quality": {"count": 0.0, "score": 0.0}, "quantity": {"count": 0, "score": 0.0}}
        }, 
        "penerimaan": {
            "tbp": {"quality": {"count": 0.0, "score": 0.0}, "quantity": {"count": 0, "score": 0.0}}, 
            "score": 0.0, "date_tbp": None , 
            "content_id": None,
            "date": {"max": None, "count": None, "score": 0.0}, 
            "last_modified": {"date": None , "count": None , "score": 0.0}, 
            "tbp_rinci": {"quality": {"count": 0.0, "score": 0.0}, "quantity": {"count": 0, "score": 0.0}}
        }, 
        "perencanaan": {
            "last_modified": {"date": None , "count": None , "score": 0.0}, 
            "rpjm": {"total_score": 0.0, "quality": {"count": 0.0, "score": 0.0}, "quantity": {"count": 0, "score": 0.0}}, 
            "score": 0.0, 
            "content_id": None,
            "rkp": {"total_score_quantity": 0.0, "total_score": 0.0, "quality_rkp5": {"count": 0.0, "score": 0.0}, "quality_rkp4": {"count": 0.0, "score": 0.0}, "quality_rkp3": {"count": 0.0, "score": 0.0}, "quality_rkp2": {"count": 0.0, "score": 0.0}, "quality_rkp1": {"count": 0.0, "score": 0.0}, "quantity_rkp2": {"count": 0, "score": 0.0}, "quantity_rkp3": {"count": 0, "score": 0.0}, "total_score_quality": 0.0, "quantity_rkp1": {"count": 0, "score": 0.0}, "quantity_rkp4": {"count": 0, "score": 0.0}, "quantity_rkp5": {"count": 0, "score": 0.0}}, 
            "renstra": {"score": 0.0}
        }, 
        "penganggaran": {
            "last_modified": {"date": None , "count": None , "score": 0.0}, 
            "score": 0.0, 
            "content_id": None,
            "rab": {"quality": {"count": 0.0, "score": 0.0}, "quantity": {"count": 0, "score": 0.0}}
        }
    }

	#Calculate Perencanaan
	cur.execute("select id, content, change_id, date_created from sd_contents where desa_id = %s and type = 'perencanaan' order by change_id desc", (desa_id,))
	sql_row_perencanaan =  cur.fetchone()

	if sql_row_perencanaan is not None:
		result["perencanaan"]["content_id"]=sql_row_perencanaan["id"]
		result["perencanaan"]["last_modified"]["date"] = str(sql_row_perencanaan["date_created"])
		result["perencanaan"]["last_modified"]["count"] = str(datetime.now() - sql_row_perencanaan["date_created"])
		result["perencanaan"]["last_modified"]["score"] = get_scale(7 -(datetime.now() - sql_row_perencanaan["date_created"]).days , 7)
		perencanaan_cur = json.loads(sql_row_perencanaan["content"], encoding='ISO-8859-1')["data"]
		renstra_tab = perencanaan_cur["renstra"]
		visi_score = get_renstra_category_score(renstra_tab, "Visi")
		misi_score = get_renstra_category_score(renstra_tab, "Misi")
		tujuan_score = get_renstra_category_score(renstra_tab, "Tujuuan")
		sasaran_score = get_renstra_category_score(renstra_tab, "Sasaran")
		result["perencanaan"]["renstra"]["score"] = (visi_score+misi_score+tujuan_score+sasaran_score) / 4.0


		rpjm_tab = perencanaan_cur["rpjm"]
		rpjm_quantity_count = len(rpjm_tab)
		rpjm_quality_count = mean([quality(row) for row in rpjm_tab])
		rpjm_score_quantity = get_scale(rpjm_quantity_count, 10)
		rpjm_score_quality = get_scale(rpjm_quality_count, 19)
		result["perencanaan"]["rpjm"]["quantity"]={"count":rpjm_quantity_count , "score" : rpjm_score_quantity}
		result["perencanaan"]["rpjm"]["quality"]= {"count": rpjm_quality_count, "score": rpjm_score_quality}
		result["perencanaan"]["rpjm"]["total_score"] = 0.4 * result["perencanaan"]["rpjm"]["quality"]["score"] + 0.6 * result["perencanaan"]["rpjm"]["quantity"]["score"]

		sum_quality_rkp = 0
		sum_quantity_rkp = 0
		for i in range (1,7):
			rkp_name="rkp"+str(i)
			rkp_tab=perencanaan_cur[rkp_name]
			rkp_quantity_count = len(rkp_tab)
			rkp_quality_count = mean([quality(row) for row in rkp_tab])
			rkp_score_quantity = get_scale(rkp_quantity_count,5)
			rkp_score_quality = get_scale(rkp_quality_count,19)
			result["perencanaan"]["rkp"]["quantity_"+rkp_name]={"count": rkp_quantity_count , "score":rkp_score_quantity }
			result["perencanaan"]["rkp"]["quality_"+rkp_name]={"count": rkp_quality_count , "score": rkp_score_quality}
			sum_quality_rkp += result["perencanaan"]["rkp"]["quality_"+rkp_name]["score"]
			sum_quantity_rkp += result["perencanaan"]["rkp"]["quantity_"+rkp_name]["score"]
		result["perencanaan"]["rkp"]["total_score_quality"] = sum_quality_rkp/6.0
		result["perencanaan"]["rkp"]["total_score_quantity"] = sum_quantity_rkp/6.0
		result["perencanaan"]["rkp"]["total_score"]=0.6*result["perencanaan"]["rkp"]["total_score_quality"] + 0.4*result["perencanaan"]["rkp"]["total_score_quantity"]

	result["perencanaan"]["score"] = 0.1 * result["perencanaan"]["renstra"]["score"] + 0.4 * result["perencanaan"]["rpjm"]["total_score"] + 0.4 * result["perencanaan"]["rkp"]["total_score"] + 0.1 * result["perencanaan"]["last_modified"]["score"]

	#Calculate Penganggaran
	cur.execute("select id, content, change_id, date_created from sd_contents where desa_id = %s and type = 'penganggaran' order by change_id desc", (desa_id,))
	sql_row_penganggaran = cur.fetchone()

	if sql_row_penganggaran is not None:
		result["penganggaran"]["content_id"]=sql_row_penganggaran["id"]
		result["penganggaran"]["last_modified"]["date"] = str(sql_row_penganggaran["date_created"])
		result["penganggaran"]["last_modified"]["count"] = str(datetime.now() - sql_row_penganggaran["date_created"])
		result["penganggaran"]["last_modified"]["score"] = get_scale(7 -(datetime.now() - sql_row_penganggaran["date_created"]).days , 7)
		penganggaran_cur = json.loads(sql_row_penganggaran["content"], encoding='ISO-8859-1')["data"]
		rab_tab= penganggaran_cur["rab"]
		rab_quantity_count = len(rab_tab)
		rab_quality_count = mean([quality(row) for row in rab_tab])
		rab_score_quantity = get_scale(rab_quantity_count,300)
		rab_score_quality = get_scale(rab_quality_count, 15)
		result["penganggaran"]["rab"]["quantity"]={"count":rab_quantity_count , "score":rab_score_quantity}
		result["penganggaran"]["rab"]["quality"]={"count":rab_quality_count, "score":rab_score_quality}
	result["penganggaran"]["score"] = 0.25 *result["penganggaran"]["rab"]["quality"]["score"] + 0.7 * result["penganggaran"]["rab"]["quantity"]["score"] + 0.05 * result["penganggaran"]["last_modified"]["score"]


	#Calculate SPP
	cur.execute("select id, content, change_id, date_created from sd_contents where desa_id = %s and type = 'spp' and subtype = '2017' order by change_id desc", (desa_id,))
	sql_row_spp = cur.fetchone()
	spp_score=result["spp"]
	spp_datas=["spp" , "spp_bukti" ,"spp_rinci"]
	spp_column_limits={"spp":8 , "spp_bukti" : 14 , "spp_rinci":7}
	spp_row_limits={"spp":80, "spp_bukti":250 ,"spp_rinci":100}
	last_modified_spp=spp_score["last_modified"]
	last_modified_spp["score"] = 0
	spp_score["score"] = 0
	if sql_row_spp is not None:
		result["spp"]["content_id"]=sql_row_spp["id"]
		last_modified_spp["date"] = str(sql_row_spp["date_created"])
		last_modified_spp["count"] = str(datetime.now() - sql_row_spp["date_created"])
		last_modified_spp["score"] = get_scale(7 -(datetime.now() - sql_row_spp["date_created"]).days , 7)
		spp_cur = json.loads(sql_row_spp["content"], encoding='ISO-8859-1')["data"]
		sum_quantity_spp=0
		sum_quality_spp=0

		for data in spp_datas:
			spp_tab=spp_cur[data]
			data_score=spp_score[data]
			row_lim_spp=spp_row_limits[data]
			col_lim_spp=spp_column_limits[data]
			spp_quantitity_count=len(spp_tab)
			spp_quality_count=mean([quality(row) for row in spp_tab])
			spp_quantity_score=get_scale(spp_quantitity_count,row_lim_spp)
			spp_quality_score=get_scale(spp_quality_count, col_lim_spp)
			data_score["quantity"]={"count": spp_quantitity_count, "score":spp_quantity_score}
			data_score["quality"]={"count":spp_quality_count, "score":spp_quality_score}
			sum_quantity_spp+=data_score["quantity"]["score"]
			sum_quality_spp+=data_score["quality"]["score"]
		spp_quantity_avg=sum_quantity_spp/3.0
		spp_quality_avg=sum_quality_spp/3.0
		spp_score_datas= 0.7*spp_quantity_avg + 0.3*spp_quality_avg
		date_spp=spp_score["date"]
		spp_cur_=spp_cur["spp"]
		date_array_str=[datetime.strptime(r[3], '%d/%m/%Y') for r in spp_cur_]
		if len(date_array_str) > 0:
		    date_spp["max"]=max(date_array_str)
		    date_spp["count"]=str(datetime.now() - date_spp["max"])
		    date_spp["score"]=get_scale(7 -(datetime.now() - date_spp["max"]).days , 7)
		    date_spp["max"]=str(date_spp["max"])
		spp_score["score"]=0.05*last_modified_spp["score"] + 0.9*spp_score_datas + 0.05*date_spp["score"]

	#Calculate Penerimaan
	cur.execute("select id, content, change_id, date_created from sd_contents where desa_id = %s and type = 'penerimaan' order by change_id desc", (desa_id,))
	sql_row_penerimaan=cur.fetchone()
	penerimaan=result["penerimaan"]
	penerimaan_datas=["tbp" , "tbp_rinci"]
	penerimaan_row_limits={"tbp": 100 , "tbp_rinci": 150}
	penerimaan_column_limits={"tbp" : 16 , "tbp_rinci" : 7 }
	last_modified_penerimaan=penerimaan["last_modified"]
	last_modified_penerimaan["score"]=0
	penerimaan["score"] = 0
	if sql_row_penerimaan is not None:
		result["penerimaan"]["content_id"]=sql_row_penerimaan["id"]
		last_modified_penerimaan["date"] = str(sql_row_penerimaan["date_created"])
		last_modified_penerimaan["count"] = str(datetime.now() - sql_row_penerimaan["date_created"])
		last_modified_penerimaan["score"] = get_scale(7 -(datetime.now() - sql_row_penerimaan["date_created"]).days , 7)
		penerimaan_cur = json.loads(sql_row_penerimaan["content"], encoding='ISO-8859-1')["data"]

		sum_quantity_penerimaan=0
		sum_quality_penerimaan=0

		for data in penerimaan_datas:
			penerimaan_tab=penerimaan_cur[data]
			data_score=penerimaan[data]
			row_lim_penerimaan=penerimaan_row_limits[data]
			col_lim_penerimaan=penerimaan_column_limits[data]
			penerimaan_quantitity_count=len(penerimaan_tab)
			penerimaan_quality_count=mean([quality(row) for row in penerimaan_tab])
			penerimaan_quantity_score=get_scale(penerimaan_quantitity_count,row_lim_penerimaan)
			penerimaan_quality_score=get_scale(penerimaan_quality_count, col_lim_penerimaan)
			data_score["quantity"]={"count": penerimaan_quantitity_count, "score":penerimaan_quantity_score}
			data_score["quality"]={"count":penerimaan_quality_count, "score":penerimaan_quality_score}
			penerimaan[data]=data_score
			sum_quantity_penerimaan+=data_score["quantity"]["score"]
			sum_quality_penerimaan+=data_score["quality"]["score"]
		penerimaan_quantity_avg=sum_quantity_penerimaan/2.0
		penerimaan_quality_avg=sum_quality_penerimaan/2.0
		penerimaan_score_datas= 0.7*penerimaan_quantity_avg + 0.3*penerimaan_quality_avg
		date_tbp=penerimaan["date"]
		tbp_cur=penerimaan_cur["tbp"]
		date_array_str_tbp=[datetime.strptime(d[3], '%d/%m/%Y') for d in tbp_cur]
		if len(date_array_str_tbp) > 0:
		    date_tbp["max"]=max(date_array_str_tbp)
		    date_tbp["count"]=str(datetime.now() - date_tbp["max"])
		    date_tbp["score"]=get_scale(7 -(datetime.now() - date_tbp["max"]).days , 7)
		    date_tbp["max"]=str(date_tbp["max"])
		penerimaan["score"]=0.05*last_modified_penerimaan["score"] + 0.9*penerimaan_score_datas + 0.05*date_tbp["score"]
	result["penerimaan"]=penerimaan

		#Calculate Total
	result["score"]=0.1*result["perencanaan"]["score"] + 0.4*result["penganggaran"]["score"] + 0.3*result["spp"]["score"] + 0.2*result["penerimaan"]["score"]
	return result
 
def get_pemetaan_statistics(cur, desa_id):
	result = {
			"score": 0.0, 
			"content_id": None, 
			"network_transportation": {"score": 0.0, "quality": {"count": 0, "score": 0}, "quantity": {"count": 0, "score": 0.0}}, 
			"waters": {"score": 0.0, "quality": {"count": 0, "score": 0}, "quantity": {"count": 0, "score": 0.0}}, 
			"facilities_infrastructures": {"score": 0.0, "quality": {"count": 0, "score": 0.0}, "quantity": {"count": 0, "score": 0.0}}, 
			"last_modified": {"date": None, "count": None, "score": 0.0}, 
			"boundary": {"score": 0.0, "quality": {"count": 0, "score": 0}, "quantity": {"count": 0, "score": 0.0}}, 
			"landuse": {"score": 0.0, "quality": {"count": 0, "score": 0.0}, "quantity": {"count": 0, "score": 0.0}}
	}
	layers = ["network_transportation", "boundary" , "landuse" , "facilities_infrastructures" , "waters"]
	layer_upper_limits = {"network_transportation": 85, "boundary":4, "landuse" :120 , "facilities_infrastructures": 1000 ,"waters" :100}

	cur.execute("select id, content, change_id, date_created from sd_contents where desa_id = %s and type = 'pemetaan' order by change_id desc", (desa_id,))
	sql_row_pemetaan = cur.fetchone()
	last_modified = result["last_modified"]
	last_modified["score"] = 0
	if sql_row_pemetaan is not None:
		result["content_id"] = sql_row_pemetaan["id"]
		last_modified["date"] = str(sql_row_pemetaan["date_created"])
		last_modified["count"] = str(datetime.now() - sql_row_pemetaan["date_created"])
		last_modified["score"] = get_scale(7 -(datetime.now() - sql_row_pemetaan["date_created"]).days , 7)
		pemetaan_cur = json.loads(sql_row_pemetaan["content"], encoding='ISO-8859-1')["data"]
		sum_quantity_pemetaan=0
		sum_quality_pemetaan=0
		#Calculate Layer
		for layer in layers:
			tab = pemetaan_cur[layer]
			layer_score = result[layer]
			layer_score["score"] = 0

			properties_filled_count = 0
			for feature in tab:
				for key in feature["properties"].keys():
					if key is not "id":
						properties_filled_count += 1
			
			quality_count = properties_filled_count
			quality = 0
			if properties_filled_count != 0:
				quality_log= math.log10(properties_filled_count)
				quality=(quality_log/3)
			quantity_count=len(tab)
			upper_limit = layer_upper_limits[layer]
			quantity=get_scale(quantity_count,upper_limit)
			layer_score["quantity"]={"count":quantity_count ,"score":quantity }
			layer_score["quality"]={"count" : quality_count , "score" : quality}
			sum_quantity_pemetaan+=layer_score["quantity"]["score"]
			sum_quality_pemetaan+=layer_score["quality"]["score"]
			layer_score["score"]=0.6*layer_score["quantity"]["score"] + 0.4*layer_score["quality"]["score"]
		avg_pemetaan_quantity=sum_quantity_pemetaan/5.0
		avg_pemetaan_quality=sum_quality_pemetaan/5.0
		pemetaan_score_datas=0.7*avg_pemetaan_quantity + 0.3*avg_pemetaan_quality
		result["score"]=0.05*last_modified["score"]+0.95*pemetaan_score_datas

	return result

def get_kemiskinan_statistics(cur, desa_id):
	result = {}
	cur.execute("select id, content, change_id, date_created from sd_contents where desa_id = %s and type = 'kemiskinan' order by change_id desc", (desa_id,))
	sql_row_kemiskinan =  cur.fetchone()
	result["last_modified_kemiskinan"] = 0
	

	return result
def get_statistics(cur, desa_id):
	result = {}
	result["scoring_formula_version"] = 2
	result["scoring_date"] = str(datetime.now())
	functions = {}
	functions["blog"] = get_blog_statistics
	functions["penduduk"] = get_penduduk_statistics
	functions["keuangan"] = get_keuangan_statistics
	functions["pemetaan"] = get_pemetaan_statistics
	for key, fn in functions.items():
		try:
			result[key]=fn(cur, desa_id)
		except Exception as e:
			print "Error on calculating %s for desa_id: %d" %(key, desa_id)
			traceback.print_exc()
	return result


if __name__ == "__main__":
	conf = open_cfg('../app.cfg')
	db = MySQLdb.connect(host=conf.MYSQL_HOST,
			     user=conf.MYSQL_USER,
			     passwd=conf.MYSQL_PASSWORD,
			     db=conf.MYSQL_DB)
	cur = db.cursor(MySQLdb.cursors.DictCursor)
	query = "select blog_id, domain from sd_desa"
	cur.execute(query)
	desas = list(cur.fetchall())
	blog_id = None
	if len(sys.argv) > 1:
		blog_id = int(sys.argv[1])
	for desa in desas:
		if blog_id is not None and desa["blog_id"] != blog_id:
			continue

		stats = get_statistics(cur, desa["blog_id"])
		stats["blog_id"] = desa["blog_id"]
		stats["domain"] = desa["domain"]
		statistics = json.dumps(stats)
		print "%d - %s" % (desa["blog_id"], desa["domain"])
		print statistics
		cur.execute("REPLACE into sd_statistics (blog_id, statistics, date) VALUES (%s, %s, now())", (desa["blog_id"], statistics))
		db.commit()
		#if "penduduk" in stats and stats["penduduk"]["score"] > 0.5:
		#	break
	db.close()

