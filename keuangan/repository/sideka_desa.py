from sqlalchemy.sql.expression import func
from base import BaseRepository
from keuangan.models import SdDesa
from keuangan.helpers import QueryHelper

class SidekaDesaRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = SdDesa

    def all_by_condition(self, has_kode=False, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        if has_kode:
            query = query.filter(self.model.kode is not None).filter(func.length(self.model.kode > 0))
        return query.all()
