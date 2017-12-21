from keuangan import db
from keuangan import ma
from base import BaseModel
from region import RegionCompleteModelSchema


class ProgressRecapitulation(BaseModel):
    __tablename__ = 'progress_recapitulations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String, nullable=False)
    budgeted_revenue = db.Column(db.DECIMAL)
    transferred_revenue = db.Column(db.DECIMAL)
    budgeted_spending = db.Column(db.DECIMAL)
    realized_spending = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='select')

    __table_args__ = (
        db.Index('pr_ix_fk_region_id', 'fk_region_id'),
    )

class ProgressRecapitulationModelSchema(ma.ModelSchema):
    class Meta:
        model = ProgressRecapitulation
        include_fk = True

    region = ma.Nested(RegionCompleteModelSchema, many=False)
