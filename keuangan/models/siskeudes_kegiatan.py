from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionModelSchema
from marshmallow import fields, post_load


class SiskeudesKegiatan(BaseModel):
    __tablename__ = 'siskeudes_kegiatans'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String)
    row_number = db.Column(db.Integer)
    id = db.Column(db.String)
    kode_bidang = db.Column(db.String)
    nama_bidang = db.Column(db.String)
    kode_kegiatan = db.Column(db.String)
    nama_kegiatan = db.Column(db.String)
    lokasi = db.Column(db.String)
    waktu = db.Column(db.String)
    nama_pptkd = db.Column(db.String)
    keluaran = db.Column(db.String)
    pagu = db.Column(db.DECIMAL)
    pagu_pak = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class SiskeudesKegiatanModelSchema(ma.ModelSchema):
    class Meta:
        model = SiskeudesKegiatan
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))


class SiskeudesKegiatanSchema(ma.Schema):
    pid = fields.Integer()
    year = fields.String()
    row_number = fields.Integer()
    id = fields.String(allow_none=True)
    kode_bidang = fields.String(allow_none=True)
    nama_bidang = fields.String(allow_none=True)
    kode_kegiatan = fields.String(allow_none=True)
    nama_kegiatan = fields.String(allow_none=True)
    lokasi = fields.String(allow_none=True)
    waktu = fields.String(allow_none=True)
    nama_pptkd = fields.String(allow_none=True)
    keluaran = fields.String(allow_none=True)
    pagu = fields.Decimal(allow_none=True)
    pagu_pak = fields.Decimal(allow_none=True)
    fk_region_id = fields.Integer()

    @post_load
    def make(self, data):
        return SiskeudesKegiatan(**data)
