from base import BaseRepository
from keuangan.models import SdDesa


class SidekaDesaRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = SdDesa

