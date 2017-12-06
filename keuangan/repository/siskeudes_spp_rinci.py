from base import BaseRepository, BaseRegionRepository, BaseSiskeudesRepository
from keuangan.models import SiskeudesSppRinci, SiskeudesSpp


class SiskeudesSppRinciRepository(BaseRepository, BaseRegionRepository, BaseSiskeudesRepository):
    def __init__(self, db):
        self.db = db
        self.model = SiskeudesSppRinci
