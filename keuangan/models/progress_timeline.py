from keuangan import db
from keuangan.models import BaseModel

class ProgressTimeline(BaseModel):
    __tablename__ = 'progress_timelines'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    apbn_key = db.Column(db.String, nullable=False)
    month = db.Column(db.Integer)
    transferred_dd = db.Column(db.DECIMAL)
    transferred_add = db.Column(db.DECIMAL)
    transferred_bhpr = db.Column(db.DECIMAL)
    realized_spending = db.Column(db.DECIMAL)

    fk_region_id = db.Column(db.String, db.ForeignKey('regions.id'))
    region = db.relationship('Region')

    def __init__(self, apbn_key, month, transferred_dd, transferred_add, transferred_bhpr, realized_spending):
        self.apbn_key = apbn_key
        self.month = month
        self.transferred_dd = transferred_dd
        self.transferred_add = transferred_add
        self.transferred_bhpr = transferred_bhpr
        self.realized_spending = realized_spending

    def __repr__(self):
        return '<ProgressTimeline %r>' % self.id

