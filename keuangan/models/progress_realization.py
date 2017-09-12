from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema


class ProgressRealization(BaseModel):
    __tablename__ = 'progress_realizations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String)
    code = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    value = db.Column(db.DECIMAL, nullable=False)
    type = db.Column(db.String, nullable=False) #Definitif,
    date = db.Column(db.Date, nullable=False)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')


class ProgressRealizationSchema(ma.ModelSchema):
    class Meta:
        model = ProgressRealization
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
