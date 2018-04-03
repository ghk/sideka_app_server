from tatakelola import db
from tatakelola import ma
from base import BaseModel
from region import RegionModelSchema
from sqlalchemy.dialects.postgresql import JSONB

class Statistic(BaseModel):
    __tablename__ = 'statistics'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Text)
    data = db.Column(JSONB)
    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')

    __table_args__ = (
        db.Index('stat_ix_fk_region_id', 'fk_region_id'),
        db.Index('stat_ix_type_fk_region_id', 'type', 'fk_region_id'),
        db.Index('stat_ix_data', 'data', postgresql_using='gin')
    )

class StatisticModelSchema(ma.ModelSchema):
    class Meta:
        model = Statistic
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
