from base import BaseRepository
from tatakelola.helpers import QueryHelper
from tatakelola.models import Boundary


class BoundaryRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = Boundary
    
    def get(self):
       return self.db.session.query(self.model).first()

    def get_by_supradesa_code(self, supradesa_code='lokpri'):
       return self.db.session.query(self.model).filter(self.model.supradesa_code == supradesa_code).first()
    
    def delete(self):
        self.db.session.query(self.model).delete()

    def delete_by_supradesa_code(self, supradesa_code='lokpri'):
        self.db.session.query(self.model).filter(self.model.supradesa_code == supradesa_code).first().delete()
