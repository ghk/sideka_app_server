from tatakelola import db
from tatakelola import ma
from base import BaseModel
from region import RegionModelSchema
from sqlalchemy.dialects.postgresql import JSONB


class Boundary(BaseModel):
    __tablename__ = 'boundaries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(JSONB)

    __table_args__ = (
        db.Index('bound_ix_data', 'data', postgresql_using='gin'),
    )


class BoundaryModelSchema(ma.ModelSchema):
    class Meta:
        model = Boundary
        include_fk = True

    region = ma.Nested(RegionModelSchema, many=False, exclude=('parent',))
