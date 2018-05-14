from base import BaseRepository
from common.helpers import QueryHelper
from tatakelola_kabupaten.models import SdAllDesa

class SidekaAllDesaRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = SdAllDesa

    def get_by_code(self, code):
        query = self.db.session.query(self.model)
        return query.filter(self.model.region_code == code and self.model.depth == 2).first()

    def get_by_prefix_depth(self, code, depth):
        query = self.db.session.query(self.model)
        return query.filter(self.model.region_code.like(code + '%')).filter(self.model.depth == depth).all()