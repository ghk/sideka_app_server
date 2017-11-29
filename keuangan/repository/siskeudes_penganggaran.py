from base import BaseRepository, BaseRegionRepository, BaseSiskeudesRepository
from keuangan.models import SiskeudesPenganggaran


class SiskeudesPenganggaranRepository(BaseRepository, BaseRegionRepository, BaseSiskeudesRepository):
    def __init__(self, db):
        self.db = db
        self.model = SiskeudesPenganggaran


    def get_total_spending_by_region_and_year(self, region_id, year):
        query = self.db.session.query(self.model) \
            .filter(self.model.kode_rekening == '5') \
            .filter(self.model.year == year)

        if (region_id != '0'):
            query = query.filter(self.model.fk_region_id == region_id)

        total = 0
        total_pak = 0
        entities = query.all()

        for entity in entities:
            if entity.anggaran is not None:
                total += entity.anggaran
            if entity.anggaran_pak is not None:
                total_pak += entity.anggaran_pak

        if total_pak > 0:
            return total_pak
        else:
            return total