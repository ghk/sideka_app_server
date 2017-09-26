from base import BaseRepository
from keuangan.models import SpendingType


class SpendingTypeRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = SpendingType
