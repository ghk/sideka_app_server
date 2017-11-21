from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionModelSchema, RegionCompleteModelSchema
from spending_type import SpendingTypeModelSchema


class SpendingRecapitulation(BaseModel):
    __tablename__ = 'spending_recapitulations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String, nullable=False)
    budgeted = db.Column(db.DECIMAL)
    realized = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')

    fk_type_id = db.Column(db.Integer, db.ForeignKey('spending_types.id'))
    type = db.relationship('SpendingType', lazy='joined')

    __table_args__ = (
        db.Index('sr_ix_fk_type_id', 'fk_type_id'),
        db.Index('sr_ix_fk_region_id', 'fk_region_id'),
        db.Index('sr_ix_fk_region_id_fk_type_id', 'fk_region_id', 'fk_type_id')
    )


class SpendingRecapitulationCompleteModelSchema(ma.ModelSchema):
    class Meta:
        model = SpendingRecapitulation
        include_fk = True

    region = ma.Nested(RegionCompleteModelSchema, many=False)
    type = ma.Nested(SpendingTypeModelSchema, many=False)


class SpendingRecapitulationModelSchema(ma.ModelSchema):
    class Meta:
        model = SpendingRecapitulation
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
    type = ma.Nested(SpendingTypeModelSchema, many=False)
