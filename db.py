from sqlalchemy import create_engine

engine = create_engine("sqlite+pysqlite:///data/coveragepy.sqlite3", future=True)
