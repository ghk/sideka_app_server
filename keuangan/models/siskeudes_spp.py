from keuangan import db
from keuangan import ma
from keuangan.helpers import CustomDateTime
from base import BaseModel
from region import RegionModelSchema


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
    region = db.relationship('Region', lazy='select')

    __table_args__ = (
        db.Index('sspp_ix_fk_region_id', 'fk_region_id'),
    )

class SiskeudesSppModelSchema(ma.ModelSchema):
    class Meta:
        model = SiskeudesSpp
        include_fk = True

    tanggal = CustomDateTime(format='keuangan', allow_none=True, missing=True)
    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))


class SiskeudesSppModelSchemaIso(ma.ModelSchema):
    class Meta:
        model = SiskeudesSpp
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))

# class SiskeudesSppSchema(ma.Schema):
#     pid = fields.Integer()
#     year = fields.String()
#     row_number = fields.Integer()
#     no = fields.String(allow_none=True)
#     kode_desa = fields.String(allow_none=True)
#     tahun = fields.String(allow_none=True)
#     tanggal = fields.Date(allow_none=True)
#     jenis = fields.String(allow_none=True)
#     keterangan = fields.String(allow_none=True)
#     jumlah = fields.Decimal(allow_none=True)
#     potongan = fields.Decimal(allow_none=True)
#     fk_region_id = fields.Integer()
