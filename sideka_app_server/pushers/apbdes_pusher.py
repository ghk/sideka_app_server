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

class ApbdesPusher(BasePusher):

	def __init__(self, desa_slug, ckan, d):
		super(ApbdesPusher, self).__init__(desa_slug, ckan, d, desa_slug + "-keuangan")
		self.apbdes = self.data_as_dicts("apbdes")


	def push_apbdes(self):
		records = self.apbdes
		fields = []
		for column in self.schema:
			typ = "text"
			fields.append({"id": column["field"], "type": typ})
		return self.ckan_push("APBDes "+self.subtyp, None, None, records, force_recreate=True, fields=fields)


	def push(self):
		print self.push_apbdes()

