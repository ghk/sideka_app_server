from tatakelola_kabupaten.models import Region
from common.helpers import QueryHelper


class RegionRepository:
    def __init__(self, db):
        self.db = db
        self.model = Region

    def get(self, id):
        return self.db.session.query(self.model) \
            .filter(self.model.id == id) \
            .first()

    def get_by_desa_id(self, desa_id):
        return self.db.session.query(self.model) \
            .filter(self.model.desa_id == desa_id) \
            .first()

    def get_all_by_kabupaten_code(self, kabupaten_code):
         return self.db.session.query(self.model) \
            .filter(self.model.id.like(kabupaten_code + '%')) \
            .all()
    
    def all(self, is_lokpri=True, page_sort_params=None):
        query = self.db.session.query(self.model) \
            .filter(self.model.is_lokpri == is_lokpri)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.all()

    def count(self, is_lokpri=True):
        return self.db.session.query(self.model) \
            .filter(self.model.is_lokpri == is_lokpri) \
            .count()

    def delete(self, id):
        query = self.db.session.query(self.model)
        return query.filter(self.model.id == id).delete()

    def add(self, entity):
        self.db.session.add(entity)
