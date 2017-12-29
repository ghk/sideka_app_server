from posyandu import db
from posyandu import ma
from base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, nullable=False)
    village = db.Column(db.String)


class UserModelSchema(ma.ModelSchema):
    class Meta:
        model = User
        include_fk = True

        # parent = ma.Nested('self', many=False, exclude=('parent', ))
