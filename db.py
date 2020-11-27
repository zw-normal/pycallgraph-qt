from sqlalchemy import create_engine

engine = create_engine(
    'sqlite+pysqlite:///data/xplan.sqlite3', echo=False, future=True)
