from base import BaseRepository, BaseRegionRepository, BaseSiskeudesRepository
from keuangan.models import SiskeudesSpp


class SiskeudesSppRepository(BaseRepository, BaseRegionRepository, BaseSiskeudesRepository):
    def __init__(self, db):
        self.db = db
        self.model = SiskeudesSpp
