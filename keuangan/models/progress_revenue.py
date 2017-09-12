from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema


class ProgressRevenue(BaseModel):
    __tablename__ = 'progress_revenues'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String)
    code = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    value = db.Column(db.DECIMAL, nullable=False)
    type = db.Column(db.String, nullable=False) # DDS, ADD, PBH
    date = db.Column(db.Date, nullable=False)
    source_name = db.Column(db.String)
    source_address = db.Column(db.String)
    source_signature = db.Column(db.String)
    account_number = db.Column(db.String)
    bank_name = db.Column(db.String)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class ProgressRevenueSchema(ma.ModelSchema):
    class Meta:
        model = ProgressRevenue
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
