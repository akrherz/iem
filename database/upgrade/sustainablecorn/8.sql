-- Storage of Tile Flow
CREATE TABLE tileflow_data(
  uniqueid varchar(24),
  plotid varchar(24),
  valid timestamptz,
  discharge_m3 real,
  discharge_m3_qcflag char(1),
  discharge_m3_qc real,
  discharge_mm real,
  discharge_mm_qcflag char(1),
  discharge_mm_qc real);
CREATE INDEX tileflow_data_idx on tileflow_data(uniqueid, plotid, valid);
GRANT SELECT on tileflow_data to nobody,apache;
