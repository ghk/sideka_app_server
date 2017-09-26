from base import BaseRepository
from siskeudes import SiskeudesRepository
from keuangan.models import SiskeudesPenganggaran


class SiskeudesPenganggaranRepository(BaseRepository, SiskeudesRepository):
    def __init__(self, db):
        self.db = db
        self.model = SiskeudesPenganggaran