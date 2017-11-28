from base import BaseRepository, BaseRegionRepository
from keuangan.models import ProgressTimeline


class ProgressTimelineRepository(BaseRepository, BaseRegionRepository):
    def __init__(self, db):
        self.db = db
        self.model = ProgressTimeline