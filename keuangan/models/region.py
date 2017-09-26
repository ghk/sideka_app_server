from keuangan import db
from keuangan import ma
from base import BaseModel


class Region(BaseModel):
    __tablename__ = 'regions'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.Text)
    type = db.Column(db.Integer, nullable=False, default=False)
    domain = db.Column(db.Text)
    url_key = db.Column(db.Text)
    is_kelurahan = db.Column(db.Boolean, nullable=False, default=False)
    is_in_scope = db.Column(db.Boolean, nullable=False, default=False)
    is_lokpri = db.Column(db.Boolean, nullable=False, default=False)

    fk_parent_id = db.Column(db.String, db.ForeignKey('regions.id'))
    parent = db.relationship('Region', remote_side=[id])

    __table_args__ = (
        db.Index('regions_ix_fk_parent_id', 'fk_parent_id'),
        db.Index('regions_ix_url_key', 'url_key'),
        db.Index('regions_ix_id_is_lokpri', 'id', 'is_lokpri'),
        db.Index('regions_ix_is_lokpri', 'is_lokpri'),
    )


class RegionModelSchema(ma.ModelSchema):
    class Meta:
        model = Region
        include_fk = True

    #parent = ma.Nested('self', many=False, exclude=('parent', ))
