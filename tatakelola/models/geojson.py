from tatakelola import db
from tatakelola import ma
from base import BaseModel
from region import RegionModelSchema
from sqlalchemy.dialects.postgresql import JSONB


class Geojson(BaseModel):
    __tablename__ = 'geojsons'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Text)
    data = db.Column(JSONB)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')

    __table_args__ = (
        db.Index('geo_ix_fk_region_id', 'fk_region_id'),
        db.Index('geo_ix_type_fk_region_id', 'type', 'fk_region_id'),
        db.Index('geo_ix_data', 'data', postgresql_using='gin')
    )


class GeojsonModelSchema(ma.ModelSchema):
    class Meta:
        model = Geojson
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
