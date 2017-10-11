from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionModelSchema
from marshmallow import fields, post_load


class SiskeudesPenganggaran(BaseModel):
    __tablename__ = 'siskeudes_penganggarans'
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


class SiskeudesPenganggaranModelSchema(ma.ModelSchema):
    class Meta:
        model = SiskeudesPenganggaran
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))


class SiskeudesPenganggaranSchema(ma.Schema):
    pid = fields.Integer()
    year = fields.String()
    row_number = fields.Integer()
    id = fields.String(allow_none=True)
    kode_kegiatan = fields.String(allow_none=True)
    kode_rekening = fields.String(allow_none=True)
    uraian = fields.String(allow_none=True)
    sumber_dana = fields.String(allow_none=True)
    satuan = fields.String(allow_none=True)
    jumlah_satuan = fields.Integer(allow_none=True)
    harga_satuan = fields.Decimal(allow_none=True)
    anggaran = fields.Decimal(allow_none=True)
    jumlah_satuan_pak = fields.Integer(allow_none=True)
    harga_satuan_pak = fields.Decimal(allow_none=True)
    anggaran_pak = fields.Decimal(allow_none=True)
    perubahan = fields.Decimal(allow_none=True)
    fk_region_id = fields.Integer()

    @post_load
    def make(self, data):
        return SiskeudesPenganggaran(**data)
