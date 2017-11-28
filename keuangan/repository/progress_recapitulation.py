from base import BaseRepository, BaseRegionRepository
from keuangan.models import ProgressRecapitulation


class ProgressRecapitulationRepository(BaseRepository, BaseRegionRepository):
    def __init__(self, db):
        self.db = db
        self.model = ProgressRecapitulation