from base import BaseRepository, BaseRegionRepository
from keuangan.models import ProgressRecapitulation
from keuangan.helpers import QueryHelper


class ProgressRecapitulationRepository(BaseRepository, BaseRegionRepository):
    def __init__(self, db):
        self.db = db
        self.model = ProgressRecapitulation
    
    def get_region_years(self, region_id):
        query = self.db.session.query(self.model)
        return [ int(p.year) for p in query \
            .filter(self.model.fk_region_id == region_id) \
            .distinct(ProgressRecapitulation.year) ]
