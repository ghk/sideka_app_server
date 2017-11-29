from base import BaseRepository, BaseRegionRepository, BaseSiskeudesRepository
from keuangan.models import SiskeudesKegiatan


class SiskeudesKegiatanRepository(BaseRepository, BaseRegionRepository, BaseSiskeudesRepository):
    def __init__(self, db):
        self.db = db
        self.model = SiskeudesKegiatan