from base import BaseRepository
from common.helpers import QueryHelper
from tatakelola_kabupaten.models import Geojson


class GeojsonRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = Geojson

    def get_by_type_and_region(self, type, region_id):
        query = self.db.session.query(self.model)
        return query.filter(self.model.type == type).filter(self.model.fk_region_id == region_id).first()

    def get_by_region(self, region_id, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.filter(self.model.fk_region_id == region_id).all()

    def get_by_type(self, type):
        query = self.db.session.query(self.model)
        return query.filter(self.model.type == type).all()

    def delete_by_region(self, region_id):
        self.db.session.query(self.model) \
            .filter(self.model.fk_region_id == region_id) \
            .delete()
