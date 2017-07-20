-- Storage of USDM
CREATE TABLE usdm(
  valid date,
  dm smallint);
select addgeometrycolumn('', 'usdm', 'geom', 4326, 'MULTIPOLYGON', 2);
CREATE INDEX usdm_valid_idx on usdm(valid);
GRANT SELECT on usdm to nobody,apache;
GRANT ALL on usdm to mesonet,ldm;
