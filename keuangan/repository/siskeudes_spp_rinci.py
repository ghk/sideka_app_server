from base import BaseRepository
from siskeudes import SiskeudesRepository
from keuangan.models import SiskeudesSppRinci, SiskeudesSpp


class SiskeudesSppRinciRepository(BaseRepository, SiskeudesRepository):
    def __init__(self, db):
        self.db = db
        self.model = SiskeudesSppRinci

    def get_full_spp_by_region(self, region_id):
        return self.db.session.query(self.model, SiskeudesSpp) \
            .join(SiskeudesSpp, self.model.no_spp == SiskeudesSpp.no) \
            .all()
