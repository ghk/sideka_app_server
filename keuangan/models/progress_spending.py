from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema


class ProgressSpending(BaseModel):
    __tablename__ = 'progress_spendings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String)
    code = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    value = db.Column(db.DECIMAL, nullable=False)
    type = db.Column(db.String, nullable=False) #Definitif,
    date = db.Column(db.Date, nullable=False)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class ProgressSpendingSchema(ma.ModelSchema):
    class Meta:
        model = ProgressSpending
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
