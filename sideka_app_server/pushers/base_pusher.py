import json
import demjson
import os

class BasePusher(object):

	def __init__(self, desa_slug, ckan, json_content, typ, subtyp, package_id):
		self.desa_slug = desa_slug
		self.ckan = ckan
		self.json_content = json_content
		self.typ = typ
		self.subtyp = subtyp
		self.package_id = package_id

		self.deserialized = json.loads(json_content)
		self.data = self.deserialized["data"]
		print len(self.data)

	def ckan_resource(self, name, keys, records):
		#resources = self.ckan.action.package_show(id=self.package_id)["resources"]
		#todo find resource and cancel push if not exists
		#for resource in resources:
			#if "name" in resource and resource["name"] == name:
			#	self.ckan.action.resource_delete(id=resource["id"])
		for rec in records:
			print rec
		return {'name': name, 'package_id': self.package_id}

	
	def ckan_push(self, name, columns, keys, records):
		resource = self.ckan_resource(name, columns, records)
		#res = self.ckan.action.datastore_create(resource=resource, records=records, primary_key=keys)
		return resource

	def data_as_dicts(self, schema_name):
		schema_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../schemas/"+schema_name+".json")
		schema = None
		with open(schema_file) as f:    
		    schema = demjson.decode(f.read())
		def to_dict(row):
			return dict((schema[i]["field"], v) for i, v in enumerate(row))
		return [to_dict(row) for row in self.data]
