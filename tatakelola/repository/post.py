from tatakelola.models import SdPostScores
from tatakelola.helpers import QueryHelper
from tatakelola.repository import SidekaDesaRepository

class PostRepository:
    def __init__(self, db):
        self.db = db
        self.model = SdPostScores

    def get_by_desa_id(self, blog_id, page_sort_params=None):
        query = self.db.session.query(self.model).filter(self.model.blog_id == blog_id)
        query = QueryHelper.build_page_sort_query(query, self.model, page_sort_params)
        return query.all()