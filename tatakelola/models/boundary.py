from tatakelola import db
from tatakelola import ma
from base import BaseModel
from region import RegionModelSchema
from sqlalchemy.dialects.postgresql import JSONB


class Boundary(BaseModel):
    __tablename__ = 'boundaries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(JSONB)
    year = db.Column(db.String, nullable=False) 
    supradesa_code = db.Column(db.String, nullable=True)

    __table_args__ = (
        db.Index('bound_ix_data', 'data', postgresql_using='gin'),
        db.Index('bound_ix_supradesa_code', 'supradesa_code', postgresql_using='btree')
    )


class BoundaryModelSchema(ma.ModelSchema):
    class Meta:
        model = Boundary
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
