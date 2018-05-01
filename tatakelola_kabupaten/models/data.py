from tatakelola_kabupaten import db
from tatakelola_kabupaten import ma
from base import BaseModel
from region import RegionModelSchema
from sqlalchemy.dialects.postgresql import JSONB


class Data(BaseModel):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(JSONB)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')

    __table_args__ = (
        db.Index('data_ix_fk_region_id', 'fk_region_id'),
        db.Index('data_ix_data', 'data', postgresql_using='gin')
    )


class DataModelSchema(ma.ModelSchema):
    class Meta:
        model = Data
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
