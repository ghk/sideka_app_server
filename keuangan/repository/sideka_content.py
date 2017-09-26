from sqlalchemy import func, and_
from base import BaseRepository
from keuangan.models import SdContent


class SidekaContentRepository(BaseRepository):
    def __init__(self, db):
        self.db = db
        self.model = SdContent

    def get_latest_content(self, type, subtype):
        subq = self.db.session.query(self.model, func.max(self.model.change_id).label('max_change_id')) \
            .filter(self.model.type == type) \
            .filter(self.model.subtype == subtype) \
            .group_by(self.model.desa_id) \
            .subquery()

        result = self.db.session.query(self.model) \
            .join(subq, and_(
            self.model.desa_id == subq.c.desa_id,
            self.model.type == subq.c.type,
            self.model.subtype == subq.c.subtype,
            self.model.change_id == subq.c.max_change_id)) \
            .all()

        return result
