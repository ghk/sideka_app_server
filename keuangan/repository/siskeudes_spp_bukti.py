from base import BaseRepository
from siskeudes import SiskeudesRepository
from keuangan.models import SiskeudesSppBukti


class SiskeudesSppBuktiRepository(BaseRepository, SiskeudesRepository):
    def __init__(self, db):
        self.db = db
        self.model = SiskeudesSppBukti