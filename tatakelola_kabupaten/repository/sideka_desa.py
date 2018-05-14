from base import BaseRepository
from common.helpers import QueryHelper
from tatakelola_kabupaten.models import SdDesa

class SidekaDesaRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = SdDesa

    def get_by_code(self, code):
        query = self.db.session.query(self.model)
        return query.filter(self.model.kode == code).first()
        
    def get_by_prefix_code(self, code):
        query = self.db.session.query(self.model)
        return query.filter(self.model.kode.like(code + '%')).all()
        
