from base import BaseRepository
from keuangan.models import SiskeudesKegiatan


class SiskeudesKegiatanRepository(BaseRepository):


    def __init__(self, db):
        self.db = db
        self.model = SiskeudesKegiatan