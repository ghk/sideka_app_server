from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionModelSchema


class SiskeudesSppRinci(BaseModel):
    __tablename__ = 'siskeudes_spp_rincis'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String)
    row_number = db.Column(db.Integer)
    kode = db.Column(db.String)
    no_spp = db.Column(db.String)
    kode_desa = db.Column(db.String)
    tahun = db.Column(db.String)
    kode_kegiatan = db.Column(db.String)
    sumber_dana = db.Column(db.String)
    nilai = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')

    spp = db.relationship('SiskeudesSpp', primaryjoin='SiskeudesSpp.no == SiskeudesSppRinci.no_spp', foreign_keys=[no_spp], lazy='joined')


class SiskeudesSppRinciModelSchema(ma.ModelSchema):
    class Meta:
        model = SiskeudesSppRinci
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
