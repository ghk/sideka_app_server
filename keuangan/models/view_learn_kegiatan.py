from keuangan import db
from keuangan import ma
from region import RegionModelSchema


class ViewLearnKegiatan(db.Model):
    __tablename__ = 'view_learn_kegiatan'
    __table_args__ = {'info': dict(is_view=True)}

    pid = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String, nullable=False)
    region_name = db.Column(db.String)
    kode_kegiatan = db.Column(db.String)
    kode_bidang = db.Column(db.String)
    uraian = db.Column(db.String)
    normalized_uraian = db.Column(db.String)
    anggaran = db.Column(db.DECIMAL)
    total_anggaran = db.Column(db.DECIMAL)
    percentage = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', foreign_keys=[fk_region_id], lazy='joined')


class ViewLearnKegiatanModelSchema(ma.ModelSchema):
    class Meta:
        model = ViewLearnKegiatan
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
