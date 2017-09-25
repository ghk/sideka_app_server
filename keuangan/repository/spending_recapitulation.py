from base import BaseRepository
from keuangan.models import SpendingRecapitulation


class SpendingRecapitulationRepository(BaseRepository):


    def __init__(self, db):
        self.db = db
        self.model = SpendingRecapitulation