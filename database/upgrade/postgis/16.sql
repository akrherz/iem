-- Storage of NLDN data, in monthly partitions!
CREATE TABLE nldn_all(
	valid timestamptz,
	geom geometry(Point, 4326),
	signal real,
	multiplicity smallint,
	axis smallint,
	eccentricity smallint,
	ellipse smallint,
	chisqr smallint);
GRANT ALL on nldn_all to mesonet,ldm;
GRANT SELECT on nldn_all to apache,nobody;

CREATE TABLE nldn2016_01(
  CONSTRAINT __nldn2016_01_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz
        and valid < '2016-02-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_01_valid_idx on nldn2016_01(valid);
GRANT ALL on nldn2016_01 to ldm,mesonet;
GRANT SELECT on nldn2016_01 to nobody,apache;
    
CREATE TABLE nldn2016_02(
  CONSTRAINT __nldn2016_02_check 
  CHECK(valid >= '2016-02-01 00:00+00'::timestamptz
        and valid < '2016-03-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_02_valid_idx on nldn2016_02(valid);
GRANT ALL on nldn2016_02 to ldm,mesonet;
GRANT SELECT on nldn2016_02 to nobody,apache;
    
CREATE TABLE nldn2016_03(
  CONSTRAINT __nldn2016_03_check 
  CHECK(valid >= '2016-03-01 00:00+00'::timestamptz
        and valid < '2016-04-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_03_valid_idx on nldn2016_03(valid);
GRANT ALL on nldn2016_03 to ldm,mesonet;
GRANT SELECT on nldn2016_03 to nobody,apache;
    
CREATE TABLE nldn2016_04(
  CONSTRAINT __nldn2016_04_check 
  CHECK(valid >= '2016-04-01 00:00+00'::timestamptz
        and valid < '2016-05-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_04_valid_idx on nldn2016_04(valid);
GRANT ALL on nldn2016_04 to ldm,mesonet;
GRANT SELECT on nldn2016_04 to nobody,apache;
    
CREATE TABLE nldn2016_05(
  CONSTRAINT __nldn2016_05_check 
  CHECK(valid >= '2016-05-01 00:00+00'::timestamptz
        and valid < '2016-06-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_05_valid_idx on nldn2016_05(valid);
GRANT ALL on nldn2016_05 to ldm,mesonet;
GRANT SELECT on nldn2016_05 to nobody,apache;
    
CREATE TABLE nldn2016_06(
  CONSTRAINT __nldn2016_06_check 
  CHECK(valid >= '2016-06-01 00:00+00'::timestamptz
        and valid < '2016-07-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_06_valid_idx on nldn2016_06(valid);
GRANT ALL on nldn2016_06 to ldm,mesonet;
GRANT SELECT on nldn2016_06 to nobody,apache;
    
CREATE TABLE nldn2016_07(
  CONSTRAINT __nldn2016_07_check 
  CHECK(valid >= '2016-07-01 00:00+00'::timestamptz
        and valid < '2016-08-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_07_valid_idx on nldn2016_07(valid);
GRANT ALL on nldn2016_07 to ldm,mesonet;
GRANT SELECT on nldn2016_07 to nobody,apache;
    
CREATE TABLE nldn2016_08(
  CONSTRAINT __nldn2016_08_check 
  CHECK(valid >= '2016-08-01 00:00+00'::timestamptz
        and valid < '2016-09-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_08_valid_idx on nldn2016_08(valid);
GRANT ALL on nldn2016_08 to ldm,mesonet;
GRANT SELECT on nldn2016_08 to nobody,apache;
    
CREATE TABLE nldn2016_09(
  CONSTRAINT __nldn2016_09_check 
  CHECK(valid >= '2016-09-01 00:00+00'::timestamptz
        and valid < '2016-10-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_09_valid_idx on nldn2016_09(valid);
GRANT ALL on nldn2016_09 to ldm,mesonet;
GRANT SELECT on nldn2016_09 to nobody,apache;
    
CREATE TABLE nldn2016_10(
  CONSTRAINT __nldn2016_10_check 
  CHECK(valid >= '2016-10-01 00:00+00'::timestamptz
        and valid < '2016-11-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_10_valid_idx on nldn2016_10(valid);
GRANT ALL on nldn2016_10 to ldm,mesonet;
GRANT SELECT on nldn2016_10 to nobody,apache;
    
CREATE TABLE nldn2016_11(
  CONSTRAINT __nldn2016_11_check 
  CHECK(valid >= '2016-11-01 00:00+00'::timestamptz
        and valid < '2016-12-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_11_valid_idx on nldn2016_11(valid);
GRANT ALL on nldn2016_11 to ldm,mesonet;
GRANT SELECT on nldn2016_11 to nobody,apache;
    
CREATE TABLE nldn2016_12(
  CONSTRAINT __nldn2016_12_check 
  CHECK(valid >= '2016-12-01 00:00+00'::timestamptz
        and valid < '2017-01-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2016_12_valid_idx on nldn2016_12(valid);
GRANT ALL on nldn2016_12 to ldm,mesonet;
GRANT SELECT on nldn2016_12 to nobody,apache;

