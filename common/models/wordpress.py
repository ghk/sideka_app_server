from common.database import db


class WpUser(db.Model):
    __tablename__ = 'wp_users'
    __bind_key__ = 'sideka'
    ID = db.Column('ID', db.Integer, primary_key=True, nullable=False)
    user_login = db.Column('user_login', db.String(length=60), nullable=False)
    user_pass = db.Column('user_pass', db.String(length=64), nullable=False)
    user_nicename = db.Column('user_nicename', db.String(length=50), nullable=False)
    user_email = db.Column('user_email', db.String(length=100), nullable=False)
    user_url = db.Column('user_url', db.String(length=100), nullable=False)
    user_registered = db.Column('user_registered', db.DateTime(timezone=False), nullable=False)
    user_activation_key = db.Column('user_activation_key', db.String(length=60), nullable=False)
    user_status = db.Column('user_status', db.Integer, nullable=False)
    display_name = db.Column('display_name', db.String(length=250), nullable=False)

    def __repr__(self):
        return '<WpUser(%r)>' % self.user_login


class WpUserMeta(db.Model):
    __tablename__ = 'wp_usermeta'
    __bind_key__ = 'sideka'
    umeta_id = db.Column('umeta_id', db.Integer, primary_key=True, nullable=False)
    meta_key = db.Column('meta_key', db.String(length=255))
    meta_value = db.Column('meta_value', db.Text(length=None))

    user_id = db.Column('user_id', db.Integer, db.ForeignKey('wp_users.ID'))
    user = db.relationship('WpUser')

    def __repr__(self):
        return '<WpUserMeta(%r, %r)>' % (self.meta_key, self.meta_value)


class WpSiteMeta(db.Model):
    __tablename__ = 'wp_sitemeta'
    __bind_key__ = 'sideka'
    meta_id = db.Column('meta_id', db.Integer, primary_key=True, nullable=False)
    site_id = db.Column('site_id', db.Integer, nullable=False)
    meta_key = db.Column('meta_key', db.String(length=255))
    meta_value = db.Column('meta_value', db.Text(length=None))

    def __repr__(self):
        return '<WpSiteMeta(%r, %r)>' % (self.meta_key, self.meta_value)


class WpBlog(db.Model):
    __tablename__ = 'wp_blogs'
    __bind_key__ = 'sideka'
    blog_id = db.Column('blog_id', db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column('site_id', db.Integer, nullable=False)
    domain = db.Column('domain', db.String(length=200), nullable=False)
    path = db.Column('path', db.String(length=100), nullable=False)
    registered = db.Column('registered', db.DateTime(timezone=False), nullable=False)
    last_updated = db.Column('last_updated', db.DateTime(timezone=False), nullable=False)
    public = db.Column('public', db.Integer, nullable=False)
    archived = db.Column('archived', db.Integer, nullable=False)
    mature = db.Column('mature', db.Integer, nullable=False)
    lang_id = db.Column('lang_id', db.Integer, nullable=False)

    def __repr__(self):
        return '<WpBlog(%r)>' % self.blog_id


