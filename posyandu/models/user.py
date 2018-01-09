from posyandu import db
from posyandu import ma
from base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String, nullable=False)
    flag = db.Column(db.Boolean)
    village = db.Column(db.String)


class UserModelSchema(ma.ModelSchema):
    class Meta:
        model = User
        include_fk = True

        # parent = ma.Nested('self', many=False, exclude=('parent', ))
