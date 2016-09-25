from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class SensorData(Base):
    __tablename__ = 'sensor_data'
    uid = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    timestamp = Column(TIMESTAMP)
    body = Column(Text)


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass