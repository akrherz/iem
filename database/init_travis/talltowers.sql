CREATE TABLE towers(
  id smallint UNIQUE NOT NULL,
  name varchar);
INSERT into towers values(0, 'Hamilton');
INSERT into towers values(1, 'Story');
GRANT SELECT on towers to nobody,apache;
GRANT ALL on towers to mesonet,ldm;

CREATE TABLE data_analog(
  tower smallint REFERENCES towers(id),
  valid timestamptz,

  ws_5m_s real,
  ws_5m_nw real,
  winddir_5m_s real,
  winddir_5m_nw real,
  rh_5m real,
  airtc_5m real,

  ws_10m_s real,
  ws_10m_nwht real,
  winddir_10m_s real,
  winddir_10m_nw real,
  rh_10m real,
  airtc_10m real,
  bp_10m real,

  ws_20m_s real,
  ws_20m_nw real,
  winddir_20m_s real,
  winddir_20m_nw real,
  rh_20m real,
  airtc_20m real,
  
  ws_40m_s real,
  ws_40m_nwht real,
  winddir_40m_s real,
  winddir_40m_nw real,
  rh_40m real,
  airtc_40m real,

  ws_80m_s real,
  ws_80m_nw real,
  winddir_80m_s real,
  winddir_80m_nw real,
  rh_80m real,
  airtc_80m real,
  bp_80m real,

  ws_120m_s real,
  ws_120m_nwht real,
  winddir_120m_s real,
  winddir_120m_nw real,
  rh_120m_1 real,
  rh_120m_2 real,
  airtc_120m_1 real,
  airtc_120m_2 real

);
GRANT ALL on data_analog to mesonet,ldm;
GRANT SELECT on data_analog to nobody,apache;
