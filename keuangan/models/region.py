from keuangan import db
from keuangan.models import BaseModel

class Region(BaseModel):
    __tablename__ = 'regions'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.Text)
    type = db.Column(db.Integer, nullable=False, default=False)
    website = db.Column(db.Text)
    url_key = db.Column(db.Text)
    is_kelurahan = db.Column(db.Boolean, nullable=False, default=False)
    is_in_scope = db.Column(db.Boolean, nullable=False, default=False)

    fk_parent_id = db.Column(db.String, db.ForeignKey('regions.id'))
    parent = db.relationship('Parent', remote_side=[id])

    def __init__(self, name, type, website, url_key, is_kelurahan, is_in_scope):
        self.name = name
        self.type = type
        self.website = website
        self.url_key = url_key
        self.is_kelurahan = is_kelurahan
        self.is_in_scope = is_in_scope

    def __repr__(self):
        return '<Region %r>' % self.id

