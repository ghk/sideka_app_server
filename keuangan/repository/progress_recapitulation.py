from base import BaseRepository
from keuangan.models import ProgressRecapitulation

class ProgressRecapitulationRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = ProgressRecapitulation
