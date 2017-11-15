from tatakelola import db
from tatakelola import ma


class ProgressRecapitulation(db.Model):
    __tablename__ = 'progress_recapitulations'
    __bind_key__ = 'keuangan'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    budgeted_revenue = db.Column(db.DECIMAL)
    transferred_revenue = db.Column(db.DECIMAL)
    budgeted_spending = db.Column(db.DECIMAL)
    realized_spending = db.Column(db.DECIMAL)
    year = db.Column(db.String, nullable=False)
    fk_region_id = db.Column(db.String)


class ProgressRecapitulationModelSchema(ma.ModelSchema):
    class Meta:
        model = ProgressRecapitulation
