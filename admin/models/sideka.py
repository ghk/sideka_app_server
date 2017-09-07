from admin import db
from datetime import datetime
from sqlalchemy.dialects.mysql import DOUBLE, BIT

class SdContent(db.Model):
    __tablename__ = 'sd_contents'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desa_id = db.Column(db.Integer)
    type = db.Column(db.String(length=50))
    subtype = db.Column(db.String(length=50))
    content = db.Column(db.Text)
    timestamp = db.Column(db.Integer)
    date_created = db.Column(db.TIMESTAMP(timezone=False), default=datetime.utcnow)
    created_by = db.Column(db.Integer)
    opendata_date_pushed = db.Column(db.DateTime(timezone=False))
    opendata_push_error = db.Column(db.String(length=200))
    change_id = db.Column(db.Integer, default=0)
    api_version = db.Column(db.String(length=4), default='1.0')

    __table_args__ = (
        db.Index('idx_type_desa_id', 'type', 'desa_id'),
        db.Index('idx_change_id', 'change_id')
    )


class SdDesa(db.Model):
    __tablename__ = 'sd_desa'
    blog_id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(length=100))
    latitude = db.Column(DOUBLE)
    longitude = db.Column(DOUBLE)
    kode = db.Column(db.String(length=50))
    desa = db.Column(db.String(length=100))
    kecamatan = db.Column(db.String(length=100))
    kabupaten = db.Column(db.String(length=100))
    propinsi = db.Column(db.String(length=100))
    kades = db.Column(db.String(length=100))
    sekdes = db.Column(db.String(length=100))
    pendamping = db.Column(db.String(length=100))
    is_dbt = db.Column(BIT(length=1))
    is_lokpri = db.Column(BIT(length=1))


class SdAllDesa(db.Model):
    __tablename__ = 'sd_all_desa'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region_code = db.Column(db.String(length=15), nullable=False)
    region_name = db.Column(db.String(length=80), nullable=False)
    parent_code = db.Column(db.String(length=15))
    depth = db.Column(db.Integer)