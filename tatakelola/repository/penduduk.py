from base import BaseRepository
from tatakelola.helpers import QueryHelper
from tatakelola.models import Penduduk


class PendudukRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = Penduduk

    def get_by_region(self, region_id, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.filter(self.model.fk_region_id == region_id).all()

    def delete_by_region(self, region_id):
        self.db.session.query(self.model) \
            .filter(self.model.fk_region_id == region_id) \
            .delete()
