from base import BaseRepository, BaseRegionRepository
from keuangan.models import BudgetRecapitulation


class BudgetRecapitulationRepository(BaseRepository, BaseRegionRepository):
    def __init__(self, db):
        self.db = db
        self.model = BudgetRecapitulation