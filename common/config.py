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
    MYSQL_DB = "wp_sideka_pati"

    KEUANGAN_POSTGRESQL_USER = "postgres"
    KEUANGAN_POSTGRESQL_PASSWORD = "postgres"
    KEUANGAN_POSTGRESQL_HOST = "database.neon.microvac:5094"
    KEUANGAN_POSTGRESQL_DB = "sideka_keuangan"

    KEUANGAN_SQLALCHEMY_DATABASE_URI = "postgresql://" + KEUANGAN_POSTGRESQL_USER + ":" + KEUANGAN_POSTGRESQL_PASSWORD + "@" + KEUANGAN_POSTGRESQL_HOST + "/" + KEUANGAN_POSTGRESQL_DB
    ADMIN_SQLALCHEMY_DATABASE_URI = "mysql://" + MYSQL_USER + ":" + MYSQL_PASSWORD + "@" + MYSQL_HOST + "/" + MYSQL_DB
    SQLALCHEMY_ECHO = True

    CKAN_HOST = "http://data.prakarsadesa.id"
    CKAN_KEY = ""
    SECRET_KEY = "microvac"


class ProductionConfig(Config):
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "ingininiinginitubanyaksekali"
    MYSQL_HOST = "database.neon.microvac"
    MYSQL_DB = "wp_sideka_pati"

    KEUANGAN_POSTGRESQL_USER = "postgres"
    KEUANGAN_POSTGRESQL_PASSWORD = "postgres"
    KEUANGAN_POSTGRESQL_HOST = "database.neon.microvac:5094"
    KEUANGAN_POSTGRESQL_DB = "sideka_keuangan"

    KEUANGAN_SQLALCHEMY_DATABASE_URI = "postgresql://" + KEUANGAN_POSTGRESQL_USER + ":" + KEUANGAN_POSTGRESQL_PASSWORD + "@" + KEUANGAN_POSTGRESQL_HOST + "/" + KEUANGAN_POSTGRESQL_DB
    ADMIN_SQLALCHEMY_DATABASE_URI = "mysql://" + MYSQL_USER + ":" + MYSQL_PASSWORD + "@" + MYSQL_HOST + "/" + MYSQL_DB
    SQLALCHEMY_ECHO = False

    CKAN_HOST = "http://data.prakarsadesa.id"
    CKAN_KEY = ""
    SECRET_KEY = "microvac"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True



