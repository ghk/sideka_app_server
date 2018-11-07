from base import BaseRepository
from tatakelola.models import SdDesa


class SidekaDesaRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = SdDesa

    def get_by_supradesa_code(self, supradesa_code, page_sort_params=None):
        query = self.db.session.query(self.model)
        query = query.filter(self.model.kode.like(supradesa_code + '%'))
        return query.all()
