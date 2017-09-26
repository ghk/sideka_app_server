from base import BaseRepository
from siskeudes import SiskeudesRepository
from keuangan.models import SiskeudesKegiatan


class SiskeudesKegiatanRepository(BaseRepository, SiskeudesRepository):
    def __init__(self, db):
        self.db = db
        self.model = SiskeudesKegiatan