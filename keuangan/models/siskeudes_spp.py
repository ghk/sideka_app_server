from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema


class SiskeudesSpp(BaseModel):
    __tablename__ = 'siskeudes_spps'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String)
    row_number = db.Column(db.Integer)
    no = db.Column(db.String)
    kode_desa = db.Column(db.String)
    tahun = db.Column(db.String)
    tanggal = db.Column(db.Date)
    jenis = db.Column(db.String)
    keterangan = db.Column(db.String)
    jumlah = db.Column(db.DECIMAL)
    potongan = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class SiskeudesSppSchema(ma.ModelSchema):
    class Meta:
        model = SiskeudesSpp
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
