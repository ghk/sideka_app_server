from keuangan import db
from datetime import datetime

class BaseModel(db.Model):
    __abstract__ = True
    date_created = db.Column(db.TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow)
    date_modified = db.Column(db.TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)