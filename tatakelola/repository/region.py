from tatakelola.models import Region
from tatakelola.helpers import QueryHelper


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

    def get_by_supradesa_code(self, supradesa_code, type=4, page_sort_params=None):
        query = self.db.session.query(self.model)

        if supradesa_code == 'lokpri':
            query = query.filter(self.model.is_lokpri == True).filter(self.model.type == type)
        else:
            query = query.filter(self.model.id.like(supradesa_code + '%')).filter(self.model.type == type)
        
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.all()
        
    def all(self, is_lokpri=True, page_sort_params=None):
        query = self.db.session.query(self.model) \
            .filter(self.model.is_lokpri == is_lokpri)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.all()

    def count(self, is_lokpri=True):
        return self.db.session.query(self.model) \
            .filter(self.model.is_lokpri == is_lokpri) \
            .count()

    def add(self, entity):
        self.db.session.add(entity)
