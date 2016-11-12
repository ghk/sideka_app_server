import MySQLdb
import itertools
import csv
import os
import types
from datetime import date
from ckanapi import RemoteCKAN

class PendudukPusher:
	
	def __init__(self, desa_slug, ckan, penduduk):
		self.desa_slug = desa_slug
		self.ckan = ckan
		self.penduduk = penduduk

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
	

	def ckan_resource(self, name, keys, records):
		resources = self.ckan.action.package_show(id=self.package_id)["resources"]
		#todo find resource and cancel push if not exists
		for resource in resources:
			if "name" in resource and resource["name"] == name:
				self.ckan.action.resource_delete(id=resource["id"])
		return {'name': name, 'package_id': package_id}

	
	def ckan_push(self, name, columns, keys, records):
		resource = self.ckan_resource(name, columns, records)
		res = self.ckan.action.datastore_create(resource=resource, records=records, primary_key=keys)
		return resource

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

	def sql_kelas_sosial(self):
		classes = set(map(lambda x: x["deskripsi"], keluarga))
		results = list()
		for klass in classes:
			row = {}
			row["tahun"] = 2015
			row["kelas_sosial"] = klass
			row["jumlah_raskin"] = len(filter(lambda k: k["deskripsi"] == klass and k["is_raskin"] == "Y", keluarga))
			row["jumlah_jamkesmas"] = len(filter(lambda k: k["deskripsi"] == klass and k["is_jamkesmas"] == "Y", keluarga))
			row["jumlah_keluarga_harapan"] = len(filter(lambda k: k["deskripsi"] == klass and k["is_pkh"] == "Y", keluarga))
			row["jumlah"] = len(filter(lambda k: k["deskripsi"] == klass, keluarga))
			results.append(row)
		return results

	def kelas_sosial(self):
		records = sql_kelas_sosial()
		print len(records)
		columns = ["tahun", "kelas_sosial", "jumlah_raskin", "jumlah_jamkesmas", "jumlah_keluarga_harapan", "jumlah"]
		keys = ["tahun", "kelas_sosial"]
		return self.ckan_push("Kelas dan Bantuan Sosial", columns, keys, records)

	def push(self):
		print self.two_columns('Pekerjaan Berdasarkan Jenis Kelamin', ['rk.deskripsi', 'rj.deskripsi'], ["pekerjaan", "jenis_kelamin"])
		print two_columns('Agama Berdasarkan Jenis Kelamin', ['ra.deskripsi', 'rj.deskripsi'], ["agama", "jenis_kelamin"])
		print two_columns('Pendidikan Berdasarkan Jenis Kelamin', ['rd.deskripsi', 'rj.deskripsi'], ["pendidikan", "jenis_kelamin"])
		print two_columns('Golongan Darah Berdasarkan Jenis Kelamin', ['rg.deskripsi', 'rj.deskripsi'], ["golongan_darah", "jenis_kelamin"])
		print two_columns('Status Kawin Berdasarkan Jenis Kelamin', ['rs.deskripsi', 'rj.deskripsi'], ["status_kawin", "jenis_kelamin"])
		print pyramid()
		print kelas_sosial()

