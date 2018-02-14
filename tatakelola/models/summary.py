from tatakelola import db
from tatakelola import ma
from base import BaseModel
from region import RegionCompleteModelSchema


class Summary(BaseModel):
    __tablename__ = 'summaries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   
    penduduk_sex_male = db.Column(db.Integer, nullable=True)
    penduduk_sex_female = db.Column(db.Integer, nullable=True)
    penduduk_sex_unknown = db.Column(db.Integer, nullable=True)
    penduduk_edu_none = db.Column(db.Integer, nullable=True)
    penduduk_edu_sd = db.Column(db.Integer, nullable=True)
    penduduk_edu_smp = db.Column(db.Integer, nullable=True)
    penduduk_edu_sma = db.Column(db.Integer, nullable=True)
    penduduk_edu_pt = db.Column(db.Integer, nullable=True)
    penduduk_job_petani = db.Column(db.Integer, nullable=True)
    penduduk_job_pedagang = db.Column(db.Integer, nullable=True)
    penduduk_job_karyawan = db.Column(db.Integer, nullable=True)
    penduduk_job_nelayan = db.Column(db.Integer, nullable=True)
    penduduk_job_lain = db.Column(db.Integer, nullable=True)

    penganggaran_budgeted_revenue = db.Column(db.DECIMAL, nullable=True)
    penganggaran_year = db.Column(db.String, nullable=True)

    pemetaan_desa_boundary = db.Column(db.DECIMAL, nullable=True)
    pemetaan_desa_circumference = db.Column(db.DECIMAL, nullable=True)
    pemetaan_dusun_total = db.Column(db.Integer, nullable=True)

    pemetaan_landuse_farmland = db.Column(db.Integer, nullable=True)
    pemetaan_landuse_forest = db.Column(db.Integer, nullable=True)
    pemetaan_landuse_orchard = db.Column(db.Integer, nullable=True)
    pemetaan_landuse_farmland_area = db.Column(db.DECIMAL, nullable=True)
    pemetaan_landuse_forest_area = db.Column(db.DECIMAL, nullable=True)
    pemetaan_landuse_orchard_area = db.Column(db.DECIMAL, nullable=True)

    pemetaan_school_tk = db.Column(db.Integer, nullable=True)
    pemetaan_school_sd = db.Column(db.Integer, nullable=True)
    pemetaan_school_smp = db.Column(db.Integer, nullable=True)
    pemetaan_school_sma = db.Column(db.Integer, nullable=True)
    pemetaan_school_pt = db.Column(db.Integer, nullable=True)

    pemetaan_highway_asphalt_length = db.Column(db.Integer, nullable=True)
    pemetaan_highway_concrete_length = db.Column(db.Integer, nullable=True)
    pemetaan_highway_other_length = db.Column(db.Integer, nullable=True)
    pemetaan_bridge_length = db.Column(db.Integer, nullable=True)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')

    __table_args__ = (
        db.Index('summaries_ix_fk_region_id', 'fk_region_id'),
    )


class SummaryModelSchema(ma.ModelSchema):
    class Meta:
        model = Summary
        include_fk = True

    region = ma.Nested(RegionCompleteModelSchema, many=False)
