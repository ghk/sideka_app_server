import MySQLdb
import itertools
import csv
import os
import types
import datetime
from datetime import date
from ckanapi import RemoteCKAN
from base_pusher import BasePusher
import demjson

class KeluargaPusher(BasePusher):

	def __init__(self, desa_slug, ckan, d):
		super(KeluargaPusher, self).__init__(desa_slug, ckan, d, desa_slug + "-kependudukan")
		self.keluarga = self.data_as_dicts("keluarga")

	def sql_kelas_sosial(self):
		classes = set(map(lambda x: x["kelas_sosial"], self.keluarga))
		results = list()
		for klass in classes:
			row = {}
			row["tahun"] = 2015
			row["kelas_sosial"] = klass
			row["jumlah_raskin"] = len(filter(lambda k: k["kelas_sosial"] == klass and k["raskin"] == "ya", self.keluarga))
			row["jumlah_keluarga_harapan"] = len(filter(lambda k: k["kelas_sosial"] == klass and k["pkh"] == "ya", self.keluarga))
			row["jumlah_bpjs"] = len(filter(lambda k: k["kelas_sosial"] == klass and k["bpjs"] == "ya", self.keluarga))
			row["jumlah_kip"] = len(filter(lambda k: k["kelas_sosial"] == klass and k["kip"] == "ya", self.keluarga))
			row["jumlah"] = len(filter(lambda k: k["kelas_sosial"] == klass, self.keluarga))
			results.append(row)
		return results

	def kelas_sosial(self):
		records = self.sql_kelas_sosial()
		print len(records)
		columns = ["tahun", "kelas_sosial", "jumlah_raskin", "jumlah_keluarga_harapan", "jumlah_bpjs", "jumlah_kip", "jumlah"]
		keys = ["tahun", "kelas_sosial"]
		delete_filters = {"tahun": 2015}
		return self.ckan_push("Kelas dan Bantuan Sosial", columns, keys, records, delete_filters=delete_filters)


	def push(self):
		print self.kelas_sosial()

