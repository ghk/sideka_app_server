from keuangan import db
from keuangan import ma
from base import BaseModel


class BudgetType(BaseModel):
    __tablename__ = 'budget_types'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    is_revenue = db.Column(db.Boolean, nullable=False)


class BudgetTypeModelSchema(ma.ModelSchema):
    class Meta:
        model = BudgetType
