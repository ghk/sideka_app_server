from posyandu import db
from posyandu import ma
from base import BaseModel


class Child(BaseModel):
    __tablename__ = 'childs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String)
    bpjs = db.Column(db.String)
    bpjs_id = db.Column(db.String)
    flag = db.Column(db.Boolean)
    village = db.Column(db.String)

    fk_parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'))
    parent = db.relationship('Parent', lazy='joined')


class ChildModelSchema(ma.ModelSchema):
    class Meta:
        model = Child
        include_fk = True


    birth_date = ma.DateTime(format='%d-%m-%Y')