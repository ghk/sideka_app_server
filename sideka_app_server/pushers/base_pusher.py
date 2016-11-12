import json
import demjson
import os
from ckanapi.errors import NotFound

class BasePusher(object):

	def __init__(self, desa_slug, ckan, d, package_id):
		self.desa_slug = desa_slug
		self.ckan = ckan
		self.json_content = d["content"]
		self.typ = d["type"]
		self.subtyp = d["subtype"]
		self.package_id = package_id
		self.desa_name = d["desa"]

		self.deserialized = json.loads(d["content"])
		self.data = self.deserialized["data"]
		#print len(self.data)

	
	def ckan_push(self, name, columns, keys, records):
		resources = self.ckan.action.package_show(id=self.package_id)["resources"]
		for resource in resources:
			if "name" in resource and resource["name"] == name:
				print "Upsert"
				self.ckan.action.datastore_upsert(resource_id=resource["id"], records=records)
				return resource
		print "Create"
		resource = {'name': name, 'package_id': self.package_id}
		res = self.ckan.action.datastore_create(resource=resource, records=records, primary_key=keys)
		return res

	def data_as_dicts(self, schema_name):
		schema_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../schemas/"+schema_name+".json")
		schema = None
		with open(schema_file) as f:    
		    schema = demjson.decode(f.read())
		def to_dict(row):
			return dict((schema[i]["field"], v) for i, v in enumerate(row))
		return [to_dict(row) for row in self.data]

	def setup(self):
		try:
			self.ckan.action.organization_show(id=self.desa_slug)
		except NotFound:
			print "Creating organization: %s %s" % (self.desa_slug, self.desa_name)
			print self.ckan.action.organization_create(id=self.desa_slug, name=self.desa_slug, title="Desa "+self.desa_name)
		package = self.desa_slug + "-kependudukan"
		try:
			self.ckan.action.package_show(id=package)
		except NotFound:
			print "Creating package: %s %s" % (package, self.desa_name)
			print self.ckan.action.package_create(id=package, name=package, title="Kependudukan Desa "+self.desa_name, owner_org=self.desa_slug)
			
