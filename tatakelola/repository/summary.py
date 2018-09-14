from base import BaseRepository
from tatakelola.helpers import QueryHelper
from tatakelola.models import Summary

class SummaryRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = Summary

    def get_by_region(self, region_id, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.filter(self.model.fk_region_id == region_id).first()

    def get_all(self, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.filter(self.model.pemetaan_desa_boundary > 0) \
            .order_by(self.model.fk_region_id) \
            .all()

    def get_by_supraadesa_code(self, supradesa_code='lokpri', page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)

        return query.order_by(self.model.supradesa_code == supradesa_code) \
            .all()

    def get_by_region_prefix(self, prefix, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)

        return query.filter(self.model.fk_region_id.like('%' + prefix + '%')).order_by(self.model.fk_region_id).all()

    def delete_by_region(self, region_id):
        self.db.session.query(self.model) \
            .filter(self.model.fk_region_id == region_id) \
            .delete()
