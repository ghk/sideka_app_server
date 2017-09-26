from marshmallow import post_load
from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionModelSchema


class SiskeudesPenerimaanRinci(BaseModel):
    __tablename__ = 'siskeudes_penerimaan_rincis'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String)
    row_number = db.Column(db.Integer)
    kode = db.Column(db.String)
    no_tbp = db.Column(db.String)
    kode_desa = db.Column(db.String)
    tahun = db.Column(db.String)
    kode_kegiatan = db.Column(db.String)
    sumber_dana = db.Column(db.String)
    nilai = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class SiskeudesPenerimaanRinciModelSchema(ma.ModelSchema):
    class Meta:
        model = SiskeudesPenerimaanRinci
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))