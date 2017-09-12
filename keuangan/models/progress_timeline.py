from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema


class ProgressTimeline(BaseModel):
    __tablename__ = 'progress_timelines'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    apbn_key = db.Column(db.String, nullable=False)
    month = db.Column(db.Integer)
    transferred_dds = db.Column(db.DECIMAL)
    transferred_add = db.Column(db.DECIMAL)
    transferred_pbh = db.Column(db.DECIMAL)
    realized_spending = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class ProgressTimelineSchema(ma.ModelSchema):
    class Meta:
        model = ProgressTimeline
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
