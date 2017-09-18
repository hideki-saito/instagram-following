import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker

import config

Base = declarative_base()


def connect(user, password, db, host='localhost', port=5432):
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return con, meta


class TimeLog(Base):
    __tablename__ = 'timelog'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    last_at = Column(Integer)
    def __repr__(self):
        return "<User(username='%s', last_at='%d')>" % (
                            self.username, self.last_at)


def create_table():
    con, metadata = connect(config.db_username, config.db_password, config.dbname)
    print (TimeLog.__table__)
    Base.metadata.create_all(con)


def update_row(username, last_at):
    con, metadata = connect(config.db_username, config.db_password, config.dbname)
    Session = sessionmaker(bind=con)
    session = Session()

    row = session.query(TimeLog).filter_by(username=username).first()
    if row:
        row.last_at = last_at
        session.commit()
    else:
        timelog = TimeLog()
        timelog.username = username
        timelog.last_at = last_at

        session.add(timelog)
        session.commit()


create_table()
update_row('test2', '124')


