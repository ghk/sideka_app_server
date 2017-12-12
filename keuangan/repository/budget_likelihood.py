from base import BaseRepository, BaseRegionRepository, BaseSiskeudesRepository
from keuangan.models import BudgetLikelihood


class BudgetLikelihoodRepository(BaseRepository, BaseRegionRepository, BaseSiskeudesRepository):
    def __init__(self, db):
        self.db = db
        self.model = BudgetLikelihood
