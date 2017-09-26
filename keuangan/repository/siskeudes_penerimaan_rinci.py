from base import BaseRepository
from siskeudes import SiskeudesRepository
from keuangan.models import SiskeudesPenerimaanRinci


class SiskeudesPenerimaanRinciRepository(BaseRepository, SiskeudesRepository):
    def __init__(self, db):
        self.db = db
        self.model = SiskeudesPenerimaanRinci