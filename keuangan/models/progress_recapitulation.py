from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema


class ProgressRecapitulation(BaseModel):
    __tablename__ = 'progress_recapitulations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transferred_revenue = db.Column(db.DECIMAL)
    realized_revenue = db.Column(db.DECIMAL)
    apbn_key = db.Column(db.String, nullable=False)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class ProgressRecapitulationSchema(ma.ModelSchema):
    class Meta:
        model = ProgressRecapitulation
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
