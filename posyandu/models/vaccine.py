from posyandu import db
from posyandu import ma
from base import BaseModel


class Vaccine(BaseModel):
    __tablename__ = 'vaccines'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    flag = db.Column(db.Boolean)
    village = db.Column(db.String)

    fk_child_id = db.Column(db.Integer, db.ForeignKey('childs.id'))
    child = db.relationship('Child', lazy='joined')

    fk_growth_id = db.Column(db.Integer, db.ForeignKey('growths.id'))
    growth = db.relationship('Growth', lazy='joined')


class VaccineModelSchema(ma.ModelSchema):
    class Meta:
        model = Vaccine
        include_fk = True

        # parent = ma.Nested('self', many=False, exclude=('parent', ))
