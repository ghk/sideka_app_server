import MySQLdb
import itertools
import csv
import os
import types
from datetime import date
from ckanapi import RemoteCKAN
from base_pusher import BasePusher
import demjson

class PendudukPusher(BasePusher):

	def __init__(self, desa_slug, ckan, json_content, typ, subtyp):
		super(PendudukPusher, self).__init__(desa_slug, ckan, json_content, typ, subtyp, desa_slug + "-kependudukan")
		self.penduduk = self.data_as_dicts("penduduk")
		print len(self.penduduk)
		print self.penduduk[0]["nik"]

	def sql_two_columns(self, columns, column_names):
		results = list()
		keyfunc = lambda r: (r[columns[0]], r[columns[1]])
		for key, group in itertools.groupby(sorted(self.penduduk,key=keyfunc), keyfunc):
			c1, c2 = key
			row = {}
			row["tahun"] = 2015
			row[column_names[0]] = c1
			row[column_names[1]] = c2
			row["jumlah"] = len(list(group))
			results.append(row)
		return results
	

	def two_columns(self, name, columns, column_names):
		records = self.sql_two_columns(columns, column_names)
		columns = ["tahun", column_names[0], column_names[1], "jumlah"]
		keys = ["tahun", column_names[0], column_names[1]]
		return self.ckan_push(name, columns, keys, records)

	def sql_pyramid(self):
		results = list()
		def calculate_age(r):
			born =  r["tanggal_lahir"]
			today = date.today()
			return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
		for r in self.penduduk:
			r["age"] = calculate_age(r)
			if r["age"] < 0:
				r["age"] = 0
		keyfunc = lambda r: (r["age"] / 5, r["rj.deskripsi"])
		for key, group in itertools.groupby(sorted(self.penduduk,key=keyfunc), keyfunc):
			age, jenkel = key
			row = {}
			row["tahun"] = 2015
			row["min_age"] = age * 5
			row["max_age"] = (age+1) * 5
			row["jenis_kelamin"] = jenkel
			row["jumlah"] = len(list(group))
			results.append(row)
		return results

	def pyramid(self):
		records = self.sql_pyramid()
		print len(records)
		columns = ["tahun", "min_age", "max_age", "jenis_kelamin", "jumlah"]
		keys = ["tahun", "min_age", "max_age", "jenis_kelamin"]
		return self.ckan_push("Kelompok Umur Berdasarkan Jenis Kelamin", columns, keys, records)


	def push(self):
		print self.two_columns('Pekerjaan Berdasarkan Jenis Kelamin', ['pekerjaan', 'jenis_kelamin'], ["pekerjaan", "jenis_kelamin"])
		print self.two_columns('Agama Berdasarkan Jenis Kelamin', ['agama', 'jenis_kelamin'], ["agama", "jenis_kelamin"])
		print self.two_columns('Pendidikan Berdasarkan Jenis Kelamin', ['pendidikan', 'jenis_kelamin'], ["pendidikan", "jenis_kelamin"])
		print self.two_columns('Golongan Darah Berdasarkan Jenis Kelamin', ['golongan_darah', 'jenis_kelamin'], ["golongan_darah", "jenis_kelamin"])
		print self.two_columns('Status Kawin Berdasarkan Jenis Kelamin', ['status_kawin', 'jenis_kelamin'], ["status_kawin", "jenis_kelamin"])
		#print self.pyramid()

