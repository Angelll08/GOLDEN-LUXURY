# Si está instalado PyMySQL (uso local en Windows), se registra como si fuera MySQLdb.
# En Render no existe y no se necesita (allí se usa PostgreSQL), por eso el try/except.
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass