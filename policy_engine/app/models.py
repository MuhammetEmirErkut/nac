from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class RadCheck(Base):
    __tablename__ = 'radcheck'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), nullable=False, default='')
    attribute = Column(String(64), nullable=False, default='')
    op = Column(String(2), nullable=False, default='==')
    value = Column(String(253), nullable=False, default='')

class RadReply(Base):
    __tablename__ = 'radreply'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), nullable=False, default='')
    attribute = Column(String(64), nullable=False, default='')
    op = Column(String(2), nullable=False, default='=')
    value = Column(String(253), nullable=False, default='')

class RadUserGroup(Base):
    __tablename__ = 'radusergroup'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), nullable=False, default='')
    groupname = Column(String(64), nullable=False, default='')
    priority = Column(Integer, nullable=False, default=1)

class RadGroupReply(Base):
    __tablename__ = 'radgroupreply'
    id = Column(Integer, primary_key=True, index=True)
    groupname = Column(String(64), nullable=False, default='')
    attribute = Column(String(64), nullable=False, default='')
    op = Column(String(2), nullable=False, default='=')
    value = Column(String(253), nullable=False, default='')

class RadAcct(Base):
    __tablename__ = 'radacct'
    radacctid = Column(BigInteger, primary_key=True, index=True)
    acctsessionid = Column(String(64), nullable=False, default='')
    acctuniqueid = Column(String(32), nullable=False, default='')
    username = Column(String(64), nullable=False, default='')
    realm = Column(String(64), default='')
    nasipaddress = Column(INET, nullable=False)
    nasportid = Column(String(32), default=None)
    nasporttype = Column(String(32), default=None)
    acctstarttime = Column(DateTime(timezone=True), nullable=True)
    acctupdatetime = Column(DateTime(timezone=True), nullable=True)
    acctstoptime = Column(DateTime(timezone=True), nullable=True)
    acctinterval = Column(Integer, nullable=True)
    acctsessiontime = Column(Integer, nullable=True)
    acctauthentic = Column(String(32), default=None)
    connectinfo_start = Column(String(128), default=None)
    connectinfo_stop = Column(String(128), default=None)
    acctinputoctets = Column(BigInteger, nullable=True)
    acctoutputoctets = Column(BigInteger, nullable=True)
    calledstationid = Column(String(50), nullable=False, default='')
    callingstationid = Column(String(50), nullable=False, default='')
    acctterminatecause = Column(String(32), nullable=False, default='')
    servicetype = Column(String(32), default=None)
    framedprotocol = Column(String(32), default=None)
    framedipaddress = Column(INET, nullable=True)
    framedipv6address = Column(INET, nullable=True)
    framedipv6prefix = Column(INET, nullable=True)
    framedinterfaceid = Column(String(44), nullable=True)
    delegatedipv6prefix = Column(INET, nullable=True)
