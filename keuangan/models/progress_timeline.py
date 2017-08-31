from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema


class ProgressTimeline(BaseModel):
    __tablename__ = 'progress_timelines'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    apbn_key = db.Column(db.String, nullable=False)
    month = db.Column(db.Integer)
    transferred_dd = db.Column(db.DECIMAL)
    transferred_add = db.Column(db.DECIMAL)
    transferred_bhpr = db.Column(db.DECIMAL)
    realized_spending = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region')

    def __repr__(self):
        return '<ProgressTimeline %r>' % self.id


class ProgressTimelineSchema(ma.ModelSchema):
    class Meta:
        model = ProgressTimeline
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
