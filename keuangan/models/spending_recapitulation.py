from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionSchema
from spending_type import SpendingTypeSchema


class SpendingRecapitulation(BaseModel):
    __tablename__ = 'spending_recapitulations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')

    fk_type_id = db.Column(db.Integer, db.ForeignKey('spending_types.id'))
    type = db.relationship('SpendingType', lazy='joined')

    __table_args__ = (
        db.Index('ix_fk_type_id', 'fk_type_id'),
        db.Index('ix_fk_region_id_fk_type_id', 'fk_region_id', 'fk_type_id')
    )


class SpendingRecapitulationSchema(ma.ModelSchema):
    class Meta:
        model = SpendingRecapitulation
        include_fk = True

    region = ma.Nested(RegionSchema, many=False, exclude=('parent',))
    type = ma.Nested(SpendingTypeSchema, many=False)
