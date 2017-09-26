from base import BaseRepository
from keuangan.models import Region
from keuangan.helpers import QueryHelper


class RegionRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = Region

    def get(self, id, is_lokpri=True):
        return self.db.session.query(self.model) \
            .filter(self.model.is_lokpri == is_lokpri) \
            .filter(self.model.id == id) \
            .first()

    def all(self, is_lokpri=True, page_sort_params=None):
        query = self.db.session.query(self.model) \
            .filter(self.model.is_lokpri == is_lokpri)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.all()

    def count(self, is_lokpri=True):
        return self.db.session.query(self.model) \
            .filter(self.model.is_lokpri == is_lokpri) \
            .count()
