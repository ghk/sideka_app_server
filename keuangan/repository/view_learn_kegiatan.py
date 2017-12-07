from base import BaseRepository, BaseRegionRepository
from keuangan.models import ViewLearnKegiatan


class ViewLearnKegiatanRepository(BaseRepository, BaseRegionRepository):
    def __init__(self, db):
        self.db = db
        self.model = ViewLearnKegiatan