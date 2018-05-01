from base import BaseRepository
from common.helpers import QueryHelper
from tatakelola_kabupaten.models import Boundary


class BoundaryRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = Boundary
    
    def get(self, kabupaten_code):
       return self.db.session.query(self.model).filter(self.model.kabupaten_code == kabupaten_code).first()

    def delete(self):
        self.db.session.query(self.model).delete()
