from base import BaseRepository
from keuangan.models import BudgetType
from keuangan.helpers import QueryHelper


class BudgetTypeRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = BudgetType

    def all_by_condition(self, is_revenue=False, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.filter(self.model.is_revenue == is_revenue).all()
