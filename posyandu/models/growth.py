from posyandu import db
from posyandu import ma
from base import BaseModel


class Growth(BaseModel):
    __tablename__ = 'growths'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    month = db.Column(db.Integer)
    weight = db.Column(db.DECIMAL)
    height = db.Column(db.Integer)
    is_breast_feeding = db.Column(db.Boolean)
    vaccine = db.Column(db.String)
    flag = db.Column(db.Boolean)
    village = db.Column(db.String)

    fk_child_id = db.Column(db.Integer, db.ForeignKey('childs.id'))
    child = db.relationship('Child', lazy='joined')


class GrowthModelSchema(ma.ModelSchema):
    class Meta:
        model = Growth
        include_fk = True

        # parent = ma.Nested('self', many=False, exclude=('parent', ))
