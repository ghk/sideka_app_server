from common.database import db
from common.marshmallow import ma
from datetime import datetime
from sqlalchemy.dialects.mysql import BIT
from sqlalchemy.sql.expression import FunctionElement
from sqlalchemy.ext.compiler import compiles

class SdContent(db.Model):
    __tablename__ = 'sd_contents'
    __bind_key__ = 'sideka'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desa_id = db.Column(db.Integer)
    type = db.Column(db.String(length=50))
    subtype = db.Column(db.String(length=50))
    content = db.Column(db.JSON)
    timestamp = db.Column(db.Integer)
    date_created = db.Column(db.TIMESTAMP(timezone=False), default=datetime.utcnow)
    created_by = db.Column(db.Integer)
    opendata_date_pushed = db.Column(db.DateTime(timezone=False))
    opendata_push_error = db.Column(db.String(length=200))
    change_id = db.Column(db.Integer, default=0)
    api_version = db.Column(db.String(length=4), default='1.0')
    content_size = db.Column(db.Integer, default=0)
    diff_size = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.Index('idx_type_desa_id', 'type', 'desa_id'),
        db.Index('idx_change_id', 'change_id')
    )


class SdContentSchema(ma.ModelSchema):
    class Meta:
        model = SdContent


class SdDesa(db.Model):
    __tablename__ = 'sd_desa'
    __bind_key__ = 'sideka'
    blog_id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(length=100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    kode = db.Column(db.String(length=50))
    desa = db.Column(db.String(length=100))
    kecamatan = db.Column(db.String(length=100))
    kabupaten = db.Column(db.String(length=100))
    propinsi = db.Column(db.String(length=100))
    kades = db.Column(db.String(length=100))
    sekdes = db.Column(db.String(length=100))
    pendamping = db.Column(db.String(length=100))
    is_dbt = db.Column(BIT)
    is_lokpri = db.Column(BIT)


class SdDesaSchema(ma.ModelSchema):
    class Meta:
        model = SdDesa


class SdAllDesa(db.Model):
    __tablename__ = 'sd_all_desa'
    __bind_key__ = 'sideka'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region_code = db.Column(db.String(length=15), nullable=False)
    region_name = db.Column(db.String(length=80), nullable=False)
    parent_code = db.Column(db.String(length=15))
    depth = db.Column(db.Integer)


class SdAllDesaSchema(ma.ModelSchema):
    class Meta:
        model = SdAllDesa


class SdStatistics(db.Model):
    __tablename__ = 'sd_statistics'
    __bind_key__ = 'sideka'
    blog_id = db.Column(db.Integer, primary_key=True)
    statistics = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)


class SdUserSupradesa(db.Model):
    __tablename__ = 'sd_users_supradesa'
    __bind_key__ = 'sideka'
    username = db.Column(db.String(length=50), primary_key=True)
    supradesa_id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(length=50))


class SdSupradesa(db.Model):
    __tablename__ = 'sd_supradesa'
    __bind_key__ = 'sideka'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region_code = db.Column(db.String(length=50), unique=True)
    flag = db.Column(db.String(length=50))
    name = db.Column(db.String(length=50))
    blog_agregate = db.Column(db.String(length=50))
    username = db.Column(db.String(length=50))
    password = db.Column(db.String(length=50))
    zoom = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


class SdSupradesaSchema(ma.ModelSchema):
    class Meta:
        model = SdSupradesa

class json_length(FunctionElement):
    name = 'json_length'

@compiles(json_length)
def compile(element, compiler, **kw):
    return "json_length(%s)" % compiler.process(element.clauses)

class json_extract(FunctionElement):
    name = 'json_extract'

@compiles(json_extract)
def compile(element, compiler, **kw):
    return "json_extract(%s)" % compiler.process(element.clauses)

class json_keys(FunctionElement):
    name = 'json_keys'

@compiles(json_keys)
def compile(element, compiler, **kw):
    return "json_keys(%s)" % compiler.process(element.clauses)

class json_unquote(FunctionElement):
    name = 'json_unquote'

@compiles(json_unquote)
def compile(element, compiler, **kw):
    return "json_unquote(%s)" % compiler.process(element.clauses)
