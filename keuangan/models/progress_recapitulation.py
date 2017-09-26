from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionModelSchema


class ProgressRecapitulation(BaseModel):
    __tablename__ = 'progress_recapitulations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    budgeted_revenue = db.Column(db.DECIMAL)
    transferred_revenue = db.Column(db.DECIMAL)
    realized_spending = db.Column(db.DECIMAL)
    year = db.Column(db.String, nullable=False)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class ProgressRecapitulationModelSchema(ma.ModelSchema):
    class Meta:
        model = ProgressRecapitulation
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
