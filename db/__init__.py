from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class DBEngine:

    def __init__(self):
        self.engine = None

    def openDataFile(self, file_name):
        # Make sure only call this function from main even loop
        self.engine = create_engine(
            'sqlite+pysqlite:///{}'.format(file_name),
            echo=False, future=True)


db_engine = DBEngine()
