from posyandu import db
from posyandu import ma
from base import BaseModel


class Parent(BaseModel):
    __tablename__ = 'parents'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    nik = db.Column(db.String)
    phone = db.Column(db.String)
    job = db.Column(db.String)
    birth_date = db.Column(db.Date)
    family_planning_date = db.Column(db.Date)
    family_planning_range = db.Column(db.String)
    flag = db.Column(db.Boolean)
    village = db.Column(db.String)

    fk_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', lazy='joined')


class ParentModelSchema(ma.ModelSchema):
    class Meta:
        model = Parent
        include_fk = True

        # parent = ma.Nested('self', many=False, exclude=('parent', ))
