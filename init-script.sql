CREATE TABLE radcheck (
  id serial PRIMARY KEY,
  username varchar(64) NOT NULL DEFAULT '',
  attribute varchar(64) NOT NULL DEFAULT '',
  op varchar(2) NOT NULL DEFAULT '==',
  value varchar(253) NOT NULL DEFAULT ''
);

CREATE TABLE radreply (
  id serial PRIMARY KEY,
  username varchar(64) NOT NULL DEFAULT '',
  attribute varchar(64) NOT NULL DEFAULT '',
  op varchar(2) NOT NULL DEFAULT '=',
  value varchar(253) NOT NULL DEFAULT ''
);

CREATE TABLE radgroupreply (
  id serial PRIMARY KEY,
  groupname varchar(64) NOT NULL DEFAULT '',
  attribute varchar(64) NOT NULL DEFAULT '',
  op varchar(2) NOT NULL DEFAULT '=',
  value varchar(253) NOT NULL DEFAULT ''
);

CREATE TABLE radusergroup (
  id serial PRIMARY KEY,
  username varchar(64) NOT NULL DEFAULT '',
  groupname varchar(64) NOT NULL DEFAULT '',
  priority int NOT NULL DEFAULT 1
);

CREATE TABLE radacct (
  radacctid bigserial PRIMARY KEY,
  acctsessionid varchar(64) NOT NULL DEFAULT '',
  acctuniqueid varchar(32) NOT NULL DEFAULT '',
  username varchar(64) NOT NULL DEFAULT '',
  realm varchar(64) DEFAULT '',
  nasipaddress inet NOT NULL,
  nasportid varchar(32) DEFAULT NULL,
  nasporttype varchar(32) DEFAULT NULL,
  acctstarttime timestamp with time zone NULL,
  acctupdatetime timestamp with time zone NULL,
  acctstoptime timestamp with time zone NULL,
  acctinterval int NULL,
  acctsessiontime int NULL,
  acctauthentic varchar(32) DEFAULT NULL,
  connectinfo_start varchar(128) DEFAULT NULL,
  connectinfo_stop varchar(128) DEFAULT NULL,
  acctinputoctets bigint NULL,
  acctoutputoctets bigint NULL,
  calledstationid varchar(50) NOT NULL DEFAULT '',
  callingstationid varchar(50) NOT NULL DEFAULT '',
  acctterminatecause varchar(32) NOT NULL DEFAULT '',
  servicetype varchar(32) DEFAULT NULL,
  framedprotocol varchar(32) DEFAULT NULL,
  framedipaddress inet NULL,
  framedipv6address inet NULL,
  framedipv6prefix inet NULL,
  framedinterfaceid varchar(44) NULL,
  delegatedipv6prefix inet NULL
);

CREATE INDEX radacct_active_session_idx ON radacct (acctsessionid, username, nasipaddress, acctstoptime);
