from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from domain.db_base import Base


class DBEngine:

    def __init__(self):
        # Default to an empty in-memory db
        self.engine = create_engine(
            'sqlite+pysqlite:///:memory:',
            echo=False,
            future=True,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool)
        Base.metadata.create_all(self.engine)

    def openDataFile(self, file_name):
        # Make sure only call this function from main even loop
        self.engine = create_engine(
            'sqlite+pysqlite:///{}'.format(file_name),
            echo=False, future=True)


db_engine = DBEngine()
