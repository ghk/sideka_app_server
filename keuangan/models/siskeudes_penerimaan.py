from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema


class SiskeudesPenerimaan(BaseModel):
    __tablename__ = 'siskeudes_penerimaans'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String)
    row_number = db.Column(db.Integer)
    id = db.Column(db.String, nullable=False)
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


class SiskeudesPenerimaanSchema(ma.ModelSchema):
    class Meta:
        model = SiskeudesPenerimaan
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
