from base import BaseRepository
from common.helpers import QueryHelper
from tatakelola_kabupaten.models import Boundary


class BoundaryRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = Boundary
    
    def get(self, code):
       return self.db.session.query(self.model).filter(self.model.code == code).first()

    def delete_by_code(self, code):
        return self.db.session.query(self.model).filter(self.model.code == code).delete()
        
    def delete(self):
        self.db.session.query(self.model).delete()
