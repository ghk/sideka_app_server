from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionModelSchema


class BudgetLikelihood(BaseModel):
    __tablename__ = 'budget_likelihoods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String, nullable=False)
    euclidean_score = db.Column(db.Float)
    rank = db.Column(db.Integer)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', foreign_keys=[fk_region_id], lazy='joined')

    fk_region_likelihood_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region_likelihood = db.relationship('Region', foreign_keys=[fk_region_likelihood_id], lazy='joined')

    __table_args__ = (
        db.Index('bl_ix_fk_region_id', 'fk_region_id'),
        db.Index('bl_ix_fk_region_likelihood_id', 'fk_region_likelihood_id')
    )


class BudgetLikelihoodModelSchema(ma.ModelSchema):
    class Meta:
        model = BudgetLikelihood
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
    region_likelihood = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
