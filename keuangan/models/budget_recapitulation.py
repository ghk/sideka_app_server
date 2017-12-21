from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionModelSchema, RegionCompleteModelSchema
from budget_type import BudgetTypeModelSchema


class BudgetRecapitulation(BaseModel):
    __tablename__ = 'budget_recapitulations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String, nullable=False)
    budgeted = db.Column(db.DECIMAL)
    realized = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='select')

    fk_type_id = db.Column(db.Integer, db.ForeignKey('budget_types.id'))
    type = db.relationship('BudgetType', lazy='select')

    __table_args__ = (
        db.Index('sr_ix_fk_type_id', 'fk_type_id'),
        db.Index('sr_ix_fk_region_id', 'fk_region_id'),
        db.Index('sr_ix_fk_region_id_fk_type_id', 'fk_region_id', 'fk_type_id')
    )


class BudgetRecapitulationModelSchema(ma.ModelSchema):
    class Meta:
        model = BudgetRecapitulation
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
    type = ma.Nested(BudgetTypeModelSchema, many=False)


class BudgetRecapitulationCompleteModelSchema(ma.ModelSchema):
    class Meta:
        model = BudgetRecapitulation
        include_fk = True

    region = ma.Nested(RegionCompleteModelSchema, many=False)
    type = ma.Nested(BudgetTypeModelSchema, many=False)
