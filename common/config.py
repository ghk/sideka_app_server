class Config(object):
    DEBUG = False
    API_VERSION = "2.0"
    HOST = "127.0.0.1"
    APP_PORT = 5001
    ADMIN_PORT = 5002
    MONITOR_PORT = 5003
    TATAKELOLA_PORT = 5004
    KEUANGAN_PORT = 5005
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "ingininiinginitubanyaksekali"
    MYSQL_HOST = "database.neon.microvac"
    MYSQL_DB = "wp_sideka_proot"
    KEUANGAN_SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@database.neon.microvac:5094/sideka_keuangan"
    ADMIN_SQLALCHEMY_DATABASE_URI = "mysql://root:ingininiinginitubanyaksekali/wp_sideka_proot"
    SQLALCHEMY_ECHO = True
    CKAN_HOST = "http://data.prakarsadesa.id"
    CKAN_KEY = ""
    SECRET_KEY = "microvac"


class ProductionConfig(Config):
    KEUANGAN_SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/sideka_keuangan"
    ADMIN_SQLALCHEMY_DATABASE_URI = "mysql://root:ingininiinginitubanyaksekali/wp_sideka_proot"
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True



