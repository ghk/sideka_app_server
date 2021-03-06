from tatakelola_kabupaten import db
from tatakelola_kabupaten import ma
from base import BaseModel
from region import RegionModelSchema
from sqlalchemy.dialects.postgresql import JSONB


class Boundary(BaseModel):
    __tablename__ = 'boundaries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String)
    data = db.Column(JSONB)
    type = db.Column(db.Integer)


    __table_args__ = (
        db.Index('bound_ix_data', 'data', postgresql_using='gin'),
        db.Index('bound_ix_code', 'code', postgresql_using='btree'),
    )


class BoundaryModelSchema(ma.ModelSchema):
    class Meta:
        model = Boundary
        include_fk = True
