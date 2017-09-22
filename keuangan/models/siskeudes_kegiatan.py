from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema


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
    waktu = db.Column(db.Date)
    nama_pptkd = db.Column(db.String)
    keluaran = db.Column(db.String)
    pagu = db.Column(db.DECIMAL)
    pagu_pak = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class SiskeudesKegiatanSchema(ma.ModelSchema):
    class Meta:
        model = SiskeudesKegiatan
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
