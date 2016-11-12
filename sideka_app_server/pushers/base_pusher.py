import json

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
