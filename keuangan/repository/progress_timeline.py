from base import BaseRepository
from keuangan.models import ProgressTimeline

class ProgressTimelineRepository(BaseRepository):


    def __init__(self, db):
        self.db = db
        self.model = ProgressTimeline


    def get_progress_timelines_by_region(self, region_id):
        return self.db.session.query(self.model)\
            .filter(ProgressTimeline.fk_region_id == region_id)\
            .all()



