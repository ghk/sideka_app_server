from base import BaseRepository
from tatakelola.helpers import QueryHelper
from tatakelola.models import Boundary


class BoundaryRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = Boundary
    
    def get(self):
       return self.db.session.query(self.model).first()

    def delete(self):
        self.db.session.query(self.model).delete()
