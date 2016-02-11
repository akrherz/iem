-- Storage of water table data
CREATE TABLE watertable_data(
  uniqueid varchar(24),
  plotid varchar(24),
  valid timestamptz,
  depth_mm real,
  depth_mm_qcflag char(1),
  depth_mm_qc real);
CREATE INDEX watertable_data_idx on watertable_data(uniqueid, plotid, valid);
GRANT SELECT on watertable_data to nobody,apache;
