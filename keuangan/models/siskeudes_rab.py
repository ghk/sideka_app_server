from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema


class SiskeudesRab(BaseModel):
    __tablename__ = 'siskeudes_rabs'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String)
    row_number = db.Column(db.Integer)
    id = db.Column(db.String)
    kode_kegiatan = db.Column(db.String)
    kode_rekening = db.Column(db.String)
    uraian = db.Column(db.String)
    sumber_dana = db.Column(db.String)
    satuan = db.Column(db.String)
    jumlah_satuan = db.Column(db.Integer)
    harga_satuan = db.Column(db.DECIMAL)
    anggaran = db.Column(db.DECIMAL)
    jumlah_satuan_pak = db.Column(db.Integer)
    harga_satuan_pak = db.Column(db.DECIMAL)
    anggaran_pak = db.Column(db.DECIMAL)
    perubahan = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class SiskeudesRabSchema(ma.ModelSchema):
    class Meta:
        model = SiskeudesRab
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
