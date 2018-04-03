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
    
    def get_pancamandala(self):
        return self.db.session.query(self.model) \
            .filter((self.model.id == '32.06.19.2009') | (self.model.id == '32.06.19.2010') | (self.model.id == '32.06.19.2011') | (self.model.id == '32.06.19.2007') | (self.model.id == '32.06.19.2006')).all()

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
