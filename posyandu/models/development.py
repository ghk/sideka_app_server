from posyandu import db
from posyandu import ma
from base import BaseModel


class Development(BaseModel):
    __tablename__ = 'developments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    position = db.Column(db.Integer)
    answer = db.Column(db.Integer)
    month = db.Column(db.Integer)
    point_b = db.Column(db.Integer)
    point_gh = db.Column(db.Integer)
    point_gk = db.Column(db.Integer)
    point_p = db.Column(db.Integer)
    point_s = db.Column(db.Integer)
    question_b = db.Column(db.String)
    question_gh = db.Column(db.String)
    question_gk = db.Column(db.String)
    question_p = db.Column(db.String)
    question_s = db.Column(db.String)
    stimulation_b = db.Column(db.String)
    stimulation_gh = db.Column(db.String)
    stimulation_gk = db.Column(db.String)
    stimulation_p = db.Column(db.String)
    stimulation_s = db.Column(db.String)
    flag = db.Column(db.Boolean)
    village = db.Column(db.String)

    fk_child_id = db.Column(db.Integer, db.ForeignKey('childs.id'))
    child = db.relationship('Child', lazy='joined')


class DevelopmentModelSchema(ma.ModelSchema):
    class Meta:
        model = Development
        include_fk = True

        # parent = ma.Nested('self', many=False, exclude=('parent', ))
