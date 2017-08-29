from keuangan import db
from keuangan.models import BaseModel

class ProgressRecapitulation(BaseModel):
    __tablename__ = 'progress_recapitulations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transferred_revenue = db.Column(db.DECIMAL)
    realized_revenue = db.Column(db.DECIMAL)
    apbn_key = db.Column(db.String, nullable=False)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region')

    def __init__(self, transfered_revenue, realized_revenue, apbn_key):
        self.transferred_revenue = transfered_revenue
        self.realized_revenue = realized_revenue
        self.apbn_key = apbn_key

    def __repr__(self):
        return '<ProgressRecapitulation %r>' % self.id

