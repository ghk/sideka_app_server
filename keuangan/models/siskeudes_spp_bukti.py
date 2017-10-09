from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionModelSchema


class SiskeudesSppBukti(BaseModel):
    __tablename__ = 'siskeudes_spp_buktis'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String)
    row_number = db.Column(db.Integer)
    no = db.Column(db.String)
    kode_rincian = db.Column(db.String)
    no_spp = db.Column(db.String)
    kode_desa = db.Column(db.String)
    tahun = db.Column(db.String)
    kode_kegiatan = db.Column(db.String)
    sumber_dana = db.Column(db.String)
    tanggal = db.Column(db.Date)
    nama_penerima = db.Column(db.String)
    nilai = db.Column(db.DECIMAL)
    rekening_bank = db.Column(db.String)
    nama_bank = db.Column(db.String)
    npwp = db.Column(db.String)
    keterangan = db.Column(db.String)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class SiskeudesSppBuktiModelSchema(ma.ModelSchema):
    class Meta:
        model = SiskeudesSppBukti
        include_fk = True

    tanggal = ma.DateTime(format='%d/%m/%Y')
    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))


class SiskeudesSppBuktiModelSchemaIso(ma.ModelSchema):
    class Meta:
        model = SiskeudesSppBukti
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
