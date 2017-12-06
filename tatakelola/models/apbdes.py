from tatakelola import db
from tatakelola import ma
from base import BaseModel
from region import RegionCompleteModelSchema


class Apbdes(BaseModel):
    __tablename__ = 'apbdes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    budgeted_revenue = db.Column(db.DECIMAL)
    transferred_revenue = db.Column(db.DECIMAL)
    budgeted_spending = db.Column(db.DECIMAL)
    realized_spending = db.Column(db.DECIMAL)
    year = db.Column(db.String, nullable=False)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region', lazy='joined')

    __table_args__ = (
        db.Index('apbdes_ix_fk_region_id', 'fk_region_id'),
    )


class ApbdesModelSchema(ma.ModelSchema):
    class Meta:
        model = Apbdes
        include_fk = True

    region = ma.Nested(RegionCompleteModelSchema, many=False)
