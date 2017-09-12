from keuangan import db
from keuangan import ma
from base import BaseModel


class SpendingType(BaseModel):
    __tablename__ = 'spending_types'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)


class SpendingTypeSchema(ma.ModelSchema):
    class Meta:
        model = SpendingType
