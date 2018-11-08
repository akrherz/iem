CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (4, now());

---
--- Store grid point geometries
---
CREATE TABLE grid(
  idx int UNIQUE,
  gridx int,
  gridy int
  );
 
 SELECT AddGeometryColumn('grid', 'geom', 4326, 'POINT', 2);
 CREATE index grid_idx on grid(idx);
 GRANT SELECT on grid to apache,nobody;
 
 ---
 --- Lookup table of observation events
 ---
 CREATE TABLE obtimes(
   valid timestamp with time zone UNIQUE
 );
 GRANT SELECT on obtimes to apache,nobody;
 
 ---
 --- Store the actual data, will have partitioned tables
 --- 
 CREATE TABLE data(
   grid_idx int REFERENCES grid(idx),
   valid timestamp with time zone,
   soil_moisture real,
   optical_depth real
 );
 GRANT SELECT on data to apache,nobody;
 
 create table data_2010_01( 
  CONSTRAINT __data_2010_01_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2010-02-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_01_grid_idx on data_2010_01(grid_idx);
CREATE INDEX data_2010_01_valid_idx on data_2010_01(valid);
GRANT SELECT on data_2010_01 to nobody,apache;


 create table data_2010_02( 
  CONSTRAINT __data_2010_02_check 
  CHECK(valid >= '2010-02-01 00:00+00'::timestamptz 
        and valid < '2010-03-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_02_grid_idx on data_2010_02(grid_idx);
CREATE INDEX data_2010_02_valid_idx on data_2010_02(valid);
GRANT SELECT on data_2010_02 to nobody,apache;


 create table data_2010_03( 
  CONSTRAINT __data_2010_03_check 
  CHECK(valid >= '2010-03-01 00:00+00'::timestamptz 
        and valid < '2010-04-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_03_grid_idx on data_2010_03(grid_idx);
CREATE INDEX data_2010_03_valid_idx on data_2010_03(valid);
GRANT SELECT on data_2010_03 to nobody,apache;


 create table data_2010_04( 
  CONSTRAINT __data_2010_04_check 
  CHECK(valid >= '2010-04-01 00:00+00'::timestamptz 
        and valid < '2010-05-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_04_grid_idx on data_2010_04(grid_idx);
CREATE INDEX data_2010_04_valid_idx on data_2010_04(valid);
GRANT SELECT on data_2010_04 to nobody,apache;


 create table data_2010_05( 
  CONSTRAINT __data_2010_05_check 
  CHECK(valid >= '2010-05-01 00:00+00'::timestamptz 
        and valid < '2010-06-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_05_grid_idx on data_2010_05(grid_idx);
CREATE INDEX data_2010_05_valid_idx on data_2010_05(valid);
GRANT SELECT on data_2010_05 to nobody,apache;


 create table data_2010_06( 
  CONSTRAINT __data_2010_06_check 
  CHECK(valid >= '2010-06-01 00:00+00'::timestamptz 
        and valid < '2010-07-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_06_grid_idx on data_2010_06(grid_idx);
CREATE INDEX data_2010_06_valid_idx on data_2010_06(valid);
GRANT SELECT on data_2010_06 to nobody,apache;


 create table data_2010_07( 
  CONSTRAINT __data_2010_07_check 
  CHECK(valid >= '2010-07-01 00:00+00'::timestamptz 
        and valid < '2010-08-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_07_grid_idx on data_2010_07(grid_idx);
CREATE INDEX data_2010_07_valid_idx on data_2010_07(valid);
GRANT SELECT on data_2010_07 to nobody,apache;


 create table data_2010_08( 
  CONSTRAINT __data_2010_08_check 
  CHECK(valid >= '2010-08-01 00:00+00'::timestamptz 
        and valid < '2010-09-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_08_grid_idx on data_2010_08(grid_idx);
CREATE INDEX data_2010_08_valid_idx on data_2010_08(valid);
GRANT SELECT on data_2010_08 to nobody,apache;


 create table data_2010_09( 
  CONSTRAINT __data_2010_09_check 
  CHECK(valid >= '2010-09-01 00:00+00'::timestamptz 
        and valid < '2010-10-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_09_grid_idx on data_2010_09(grid_idx);
CREATE INDEX data_2010_09_valid_idx on data_2010_09(valid);
GRANT SELECT on data_2010_09 to nobody,apache;


 create table data_2010_10( 
  CONSTRAINT __data_2010_10_check 
  CHECK(valid >= '2010-10-01 00:00+00'::timestamptz 
        and valid < '2010-11-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_10_grid_idx on data_2010_10(grid_idx);
CREATE INDEX data_2010_10_valid_idx on data_2010_10(valid);
GRANT SELECT on data_2010_10 to nobody,apache;


 create table data_2010_11( 
  CONSTRAINT __data_2010_11_check 
  CHECK(valid >= '2010-11-01 00:00+00'::timestamptz 
        and valid < '2010-12-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_11_grid_idx on data_2010_11(grid_idx);
CREATE INDEX data_2010_11_valid_idx on data_2010_11(valid);
GRANT SELECT on data_2010_11 to nobody,apache;


 create table data_2010_12( 
  CONSTRAINT __data_2010_12_check 
  CHECK(valid >= '2010-12-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2010_12_grid_idx on data_2010_12(grid_idx);
CREATE INDEX data_2010_12_valid_idx on data_2010_12(valid);
GRANT SELECT on data_2010_12 to nobody,apache;


 create table data_2011_01( 
  CONSTRAINT __data_2011_01_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2011-02-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_01_grid_idx on data_2011_01(grid_idx);
CREATE INDEX data_2011_01_valid_idx on data_2011_01(valid);
GRANT SELECT on data_2011_01 to nobody,apache;


 create table data_2011_02( 
  CONSTRAINT __data_2011_02_check 
  CHECK(valid >= '2011-02-01 00:00+00'::timestamptz 
        and valid < '2011-03-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_02_grid_idx on data_2011_02(grid_idx);
CREATE INDEX data_2011_02_valid_idx on data_2011_02(valid);
GRANT SELECT on data_2011_02 to nobody,apache;


 create table data_2011_03( 
  CONSTRAINT __data_2011_03_check 
  CHECK(valid >= '2011-03-01 00:00+00'::timestamptz 
        and valid < '2011-04-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_03_grid_idx on data_2011_03(grid_idx);
CREATE INDEX data_2011_03_valid_idx on data_2011_03(valid);
GRANT SELECT on data_2011_03 to nobody,apache;


 create table data_2011_04( 
  CONSTRAINT __data_2011_04_check 
  CHECK(valid >= '2011-04-01 00:00+00'::timestamptz 
        and valid < '2011-05-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_04_grid_idx on data_2011_04(grid_idx);
CREATE INDEX data_2011_04_valid_idx on data_2011_04(valid);
GRANT SELECT on data_2011_04 to nobody,apache;


 create table data_2011_05( 
  CONSTRAINT __data_2011_05_check 
  CHECK(valid >= '2011-05-01 00:00+00'::timestamptz 
        and valid < '2011-06-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_05_grid_idx on data_2011_05(grid_idx);
CREATE INDEX data_2011_05_valid_idx on data_2011_05(valid);
GRANT SELECT on data_2011_05 to nobody,apache;


 create table data_2011_06( 
  CONSTRAINT __data_2011_06_check 
  CHECK(valid >= '2011-06-01 00:00+00'::timestamptz 
        and valid < '2011-07-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_06_grid_idx on data_2011_06(grid_idx);
CREATE INDEX data_2011_06_valid_idx on data_2011_06(valid);
GRANT SELECT on data_2011_06 to nobody,apache;


 create table data_2011_07( 
  CONSTRAINT __data_2011_07_check 
  CHECK(valid >= '2011-07-01 00:00+00'::timestamptz 
        and valid < '2011-08-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_07_grid_idx on data_2011_07(grid_idx);
CREATE INDEX data_2011_07_valid_idx on data_2011_07(valid);
GRANT SELECT on data_2011_07 to nobody,apache;


 create table data_2011_08( 
  CONSTRAINT __data_2011_08_check 
  CHECK(valid >= '2011-08-01 00:00+00'::timestamptz 
        and valid < '2011-09-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_08_grid_idx on data_2011_08(grid_idx);
CREATE INDEX data_2011_08_valid_idx on data_2011_08(valid);
GRANT SELECT on data_2011_08 to nobody,apache;


 create table data_2011_09( 
  CONSTRAINT __data_2011_09_check 
  CHECK(valid >= '2011-09-01 00:00+00'::timestamptz 
        and valid < '2011-10-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_09_grid_idx on data_2011_09(grid_idx);
CREATE INDEX data_2011_09_valid_idx on data_2011_09(valid);
GRANT SELECT on data_2011_09 to nobody,apache;


 create table data_2011_10( 
  CONSTRAINT __data_2011_10_check 
  CHECK(valid >= '2011-10-01 00:00+00'::timestamptz 
        and valid < '2011-11-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_10_grid_idx on data_2011_10(grid_idx);
CREATE INDEX data_2011_10_valid_idx on data_2011_10(valid);
GRANT SELECT on data_2011_10 to nobody,apache;


 create table data_2011_11( 
  CONSTRAINT __data_2011_11_check 
  CHECK(valid >= '2011-11-01 00:00+00'::timestamptz 
        and valid < '2011-12-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_11_grid_idx on data_2011_11(grid_idx);
CREATE INDEX data_2011_11_valid_idx on data_2011_11(valid);
GRANT SELECT on data_2011_11 to nobody,apache;


 create table data_2011_12( 
  CONSTRAINT __data_2011_12_check 
  CHECK(valid >= '2011-12-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2011_12_grid_idx on data_2011_12(grid_idx);
CREATE INDEX data_2011_12_valid_idx on data_2011_12(valid);
GRANT SELECT on data_2011_12 to nobody,apache;


 create table data_2012_01( 
  CONSTRAINT __data_2012_01_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2012-02-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_01_grid_idx on data_2012_01(grid_idx);
CREATE INDEX data_2012_01_valid_idx on data_2012_01(valid);
GRANT SELECT on data_2012_01 to nobody,apache;


 create table data_2012_02( 
  CONSTRAINT __data_2012_02_check 
  CHECK(valid >= '2012-02-01 00:00+00'::timestamptz 
        and valid < '2012-03-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_02_grid_idx on data_2012_02(grid_idx);
CREATE INDEX data_2012_02_valid_idx on data_2012_02(valid);
GRANT SELECT on data_2012_02 to nobody,apache;


 create table data_2012_03( 
  CONSTRAINT __data_2012_03_check 
  CHECK(valid >= '2012-03-01 00:00+00'::timestamptz 
        and valid < '2012-04-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_03_grid_idx on data_2012_03(grid_idx);
CREATE INDEX data_2012_03_valid_idx on data_2012_03(valid);
GRANT SELECT on data_2012_03 to nobody,apache;


 create table data_2012_04( 
  CONSTRAINT __data_2012_04_check 
  CHECK(valid >= '2012-04-01 00:00+00'::timestamptz 
        and valid < '2012-05-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_04_grid_idx on data_2012_04(grid_idx);
CREATE INDEX data_2012_04_valid_idx on data_2012_04(valid);
GRANT SELECT on data_2012_04 to nobody,apache;


 create table data_2012_05( 
  CONSTRAINT __data_2012_05_check 
  CHECK(valid >= '2012-05-01 00:00+00'::timestamptz 
        and valid < '2012-06-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_05_grid_idx on data_2012_05(grid_idx);
CREATE INDEX data_2012_05_valid_idx on data_2012_05(valid);
GRANT SELECT on data_2012_05 to nobody,apache;


 create table data_2012_06( 
  CONSTRAINT __data_2012_06_check 
  CHECK(valid >= '2012-06-01 00:00+00'::timestamptz 
        and valid < '2012-07-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_06_grid_idx on data_2012_06(grid_idx);
CREATE INDEX data_2012_06_valid_idx on data_2012_06(valid);
GRANT SELECT on data_2012_06 to nobody,apache;


 create table data_2012_07( 
  CONSTRAINT __data_2012_07_check 
  CHECK(valid >= '2012-07-01 00:00+00'::timestamptz 
        and valid < '2012-08-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_07_grid_idx on data_2012_07(grid_idx);
CREATE INDEX data_2012_07_valid_idx on data_2012_07(valid);
GRANT SELECT on data_2012_07 to nobody,apache;


 create table data_2012_08( 
  CONSTRAINT __data_2012_08_check 
  CHECK(valid >= '2012-08-01 00:00+00'::timestamptz 
        and valid < '2012-09-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_08_grid_idx on data_2012_08(grid_idx);
CREATE INDEX data_2012_08_valid_idx on data_2012_08(valid);
GRANT SELECT on data_2012_08 to nobody,apache;


 create table data_2012_09( 
  CONSTRAINT __data_2012_09_check 
  CHECK(valid >= '2012-09-01 00:00+00'::timestamptz 
        and valid < '2012-10-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_09_grid_idx on data_2012_09(grid_idx);
CREATE INDEX data_2012_09_valid_idx on data_2012_09(valid);
GRANT SELECT on data_2012_09 to nobody,apache;


 create table data_2012_10( 
  CONSTRAINT __data_2012_10_check 
  CHECK(valid >= '2012-10-01 00:00+00'::timestamptz 
        and valid < '2012-11-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_10_grid_idx on data_2012_10(grid_idx);
CREATE INDEX data_2012_10_valid_idx on data_2012_10(valid);
GRANT SELECT on data_2012_10 to nobody,apache;


 create table data_2012_11( 
  CONSTRAINT __data_2012_11_check 
  CHECK(valid >= '2012-11-01 00:00+00'::timestamptz 
        and valid < '2012-12-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_11_grid_idx on data_2012_11(grid_idx);
CREATE INDEX data_2012_11_valid_idx on data_2012_11(valid);
GRANT SELECT on data_2012_11 to nobody,apache;


 create table data_2012_12( 
  CONSTRAINT __data_2012_12_check 
  CHECK(valid >= '2012-12-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2012_12_grid_idx on data_2012_12(grid_idx);
CREATE INDEX data_2012_12_valid_idx on data_2012_12(valid);
GRANT SELECT on data_2012_12 to nobody,apache;


 create table data_2013_01( 
  CONSTRAINT __data_2013_01_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2013-02-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_01_grid_idx on data_2013_01(grid_idx);
CREATE INDEX data_2013_01_valid_idx on data_2013_01(valid);
GRANT SELECT on data_2013_01 to nobody,apache;


 create table data_2013_02( 
  CONSTRAINT __data_2013_02_check 
  CHECK(valid >= '2013-02-01 00:00+00'::timestamptz 
        and valid < '2013-03-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_02_grid_idx on data_2013_02(grid_idx);
CREATE INDEX data_2013_02_valid_idx on data_2013_02(valid);
GRANT SELECT on data_2013_02 to nobody,apache;


 create table data_2013_03( 
  CONSTRAINT __data_2013_03_check 
  CHECK(valid >= '2013-03-01 00:00+00'::timestamptz 
        and valid < '2013-04-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_03_grid_idx on data_2013_03(grid_idx);
CREATE INDEX data_2013_03_valid_idx on data_2013_03(valid);
GRANT SELECT on data_2013_03 to nobody,apache;


 create table data_2013_04( 
  CONSTRAINT __data_2013_04_check 
  CHECK(valid >= '2013-04-01 00:00+00'::timestamptz 
        and valid < '2013-05-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_04_grid_idx on data_2013_04(grid_idx);
CREATE INDEX data_2013_04_valid_idx on data_2013_04(valid);
GRANT SELECT on data_2013_04 to nobody,apache;


 create table data_2013_05( 
  CONSTRAINT __data_2013_05_check 
  CHECK(valid >= '2013-05-01 00:00+00'::timestamptz 
        and valid < '2013-06-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_05_grid_idx on data_2013_05(grid_idx);
CREATE INDEX data_2013_05_valid_idx on data_2013_05(valid);
GRANT SELECT on data_2013_05 to nobody,apache;


 create table data_2013_06( 
  CONSTRAINT __data_2013_06_check 
  CHECK(valid >= '2013-06-01 00:00+00'::timestamptz 
        and valid < '2013-07-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_06_grid_idx on data_2013_06(grid_idx);
CREATE INDEX data_2013_06_valid_idx on data_2013_06(valid);
GRANT SELECT on data_2013_06 to nobody,apache;


 create table data_2013_07( 
  CONSTRAINT __data_2013_07_check 
  CHECK(valid >= '2013-07-01 00:00+00'::timestamptz 
        and valid < '2013-08-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_07_grid_idx on data_2013_07(grid_idx);
CREATE INDEX data_2013_07_valid_idx on data_2013_07(valid);
GRANT SELECT on data_2013_07 to nobody,apache;


 create table data_2013_08( 
  CONSTRAINT __data_2013_08_check 
  CHECK(valid >= '2013-08-01 00:00+00'::timestamptz 
        and valid < '2013-09-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_08_grid_idx on data_2013_08(grid_idx);
CREATE INDEX data_2013_08_valid_idx on data_2013_08(valid);
GRANT SELECT on data_2013_08 to nobody,apache;


 create table data_2013_09( 
  CONSTRAINT __data_2013_09_check 
  CHECK(valid >= '2013-09-01 00:00+00'::timestamptz 
        and valid < '2013-10-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_09_grid_idx on data_2013_09(grid_idx);
CREATE INDEX data_2013_09_valid_idx on data_2013_09(valid);
GRANT SELECT on data_2013_09 to nobody,apache;


 create table data_2013_10( 
  CONSTRAINT __data_2013_10_check 
  CHECK(valid >= '2013-10-01 00:00+00'::timestamptz 
        and valid < '2013-11-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_10_grid_idx on data_2013_10(grid_idx);
CREATE INDEX data_2013_10_valid_idx on data_2013_10(valid);
GRANT SELECT on data_2013_10 to nobody,apache;


 create table data_2013_11( 
  CONSTRAINT __data_2013_11_check 
  CHECK(valid >= '2013-11-01 00:00+00'::timestamptz 
        and valid < '2013-12-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_11_grid_idx on data_2013_11(grid_idx);
CREATE INDEX data_2013_11_valid_idx on data_2013_11(valid);
GRANT SELECT on data_2013_11 to nobody,apache;


 create table data_2013_12( 
  CONSTRAINT __data_2013_12_check 
  CHECK(valid >= '2013-12-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2013_12_grid_idx on data_2013_12(grid_idx);
CREATE INDEX data_2013_12_valid_idx on data_2013_12(valid);
GRANT SELECT on data_2013_12 to nobody,apache;


 create table data_2014_01( 
  CONSTRAINT __data_2014_01_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2014-02-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_01_grid_idx on data_2014_01(grid_idx);
CREATE INDEX data_2014_01_valid_idx on data_2014_01(valid);
GRANT SELECT on data_2014_01 to nobody,apache;


 create table data_2014_02( 
  CONSTRAINT __data_2014_02_check 
  CHECK(valid >= '2014-02-01 00:00+00'::timestamptz 
        and valid < '2014-03-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_02_grid_idx on data_2014_02(grid_idx);
CREATE INDEX data_2014_02_valid_idx on data_2014_02(valid);
GRANT SELECT on data_2014_02 to nobody,apache;


 create table data_2014_03( 
  CONSTRAINT __data_2014_03_check 
  CHECK(valid >= '2014-03-01 00:00+00'::timestamptz 
        and valid < '2014-04-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_03_grid_idx on data_2014_03(grid_idx);
CREATE INDEX data_2014_03_valid_idx on data_2014_03(valid);
GRANT SELECT on data_2014_03 to nobody,apache;


 create table data_2014_04( 
  CONSTRAINT __data_2014_04_check 
  CHECK(valid >= '2014-04-01 00:00+00'::timestamptz 
        and valid < '2014-05-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_04_grid_idx on data_2014_04(grid_idx);
CREATE INDEX data_2014_04_valid_idx on data_2014_04(valid);
GRANT SELECT on data_2014_04 to nobody,apache;


 create table data_2014_05( 
  CONSTRAINT __data_2014_05_check 
  CHECK(valid >= '2014-05-01 00:00+00'::timestamptz 
        and valid < '2014-06-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_05_grid_idx on data_2014_05(grid_idx);
CREATE INDEX data_2014_05_valid_idx on data_2014_05(valid);
GRANT SELECT on data_2014_05 to nobody,apache;


 create table data_2014_06( 
  CONSTRAINT __data_2014_06_check 
  CHECK(valid >= '2014-06-01 00:00+00'::timestamptz 
        and valid < '2014-07-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_06_grid_idx on data_2014_06(grid_idx);
CREATE INDEX data_2014_06_valid_idx on data_2014_06(valid);
GRANT SELECT on data_2014_06 to nobody,apache;


 create table data_2014_07( 
  CONSTRAINT __data_2014_07_check 
  CHECK(valid >= '2014-07-01 00:00+00'::timestamptz 
        and valid < '2014-08-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_07_grid_idx on data_2014_07(grid_idx);
CREATE INDEX data_2014_07_valid_idx on data_2014_07(valid);
GRANT SELECT on data_2014_07 to nobody,apache;


 create table data_2014_08( 
  CONSTRAINT __data_2014_08_check 
  CHECK(valid >= '2014-08-01 00:00+00'::timestamptz 
        and valid < '2014-09-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_08_grid_idx on data_2014_08(grid_idx);
CREATE INDEX data_2014_08_valid_idx on data_2014_08(valid);
GRANT SELECT on data_2014_08 to nobody,apache;


 create table data_2014_09( 
  CONSTRAINT __data_2014_09_check 
  CHECK(valid >= '2014-09-01 00:00+00'::timestamptz 
        and valid < '2014-10-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_09_grid_idx on data_2014_09(grid_idx);
CREATE INDEX data_2014_09_valid_idx on data_2014_09(valid);
GRANT SELECT on data_2014_09 to nobody,apache;


 create table data_2014_10( 
  CONSTRAINT __data_2014_10_check 
  CHECK(valid >= '2014-10-01 00:00+00'::timestamptz 
        and valid < '2014-11-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_10_grid_idx on data_2014_10(grid_idx);
CREATE INDEX data_2014_10_valid_idx on data_2014_10(valid);
GRANT SELECT on data_2014_10 to nobody,apache;


 create table data_2014_11( 
  CONSTRAINT __data_2014_11_check 
  CHECK(valid >= '2014-11-01 00:00+00'::timestamptz 
        and valid < '2014-12-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_11_grid_idx on data_2014_11(grid_idx);
CREATE INDEX data_2014_11_valid_idx on data_2014_11(valid);
GRANT SELECT on data_2014_11 to nobody,apache;


 create table data_2014_12( 
  CONSTRAINT __data_2014_12_check 
  CHECK(valid >= '2014-12-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2014_12_grid_idx on data_2014_12(grid_idx);
CREATE INDEX data_2014_12_valid_idx on data_2014_12(valid);
GRANT SELECT on data_2014_12 to nobody,apache;

 create table data_2015_01( 
  CONSTRAINT __data_2015_01_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2015-02-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_01_grid_idx on data_2015_01(grid_idx);
CREATE INDEX data_2015_01_valid_idx on data_2015_01(valid);
GRANT SELECT on data_2015_01 to nobody,apache;


 create table data_2015_02( 
  CONSTRAINT __data_2015_02_check 
  CHECK(valid >= '2015-02-01 00:00+00'::timestamptz 
        and valid < '2015-03-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_02_grid_idx on data_2015_02(grid_idx);
CREATE INDEX data_2015_02_valid_idx on data_2015_02(valid);
GRANT SELECT on data_2015_02 to nobody,apache;


 create table data_2015_03( 
  CONSTRAINT __data_2015_03_check 
  CHECK(valid >= '2015-03-01 00:00+00'::timestamptz 
        and valid < '2015-04-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_03_grid_idx on data_2015_03(grid_idx);
CREATE INDEX data_2015_03_valid_idx on data_2015_03(valid);
GRANT SELECT on data_2015_03 to nobody,apache;


 create table data_2015_04( 
  CONSTRAINT __data_2015_04_check 
  CHECK(valid >= '2015-04-01 00:00+00'::timestamptz 
        and valid < '2015-05-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_04_grid_idx on data_2015_04(grid_idx);
CREATE INDEX data_2015_04_valid_idx on data_2015_04(valid);
GRANT SELECT on data_2015_04 to nobody,apache;


 create table data_2015_05( 
  CONSTRAINT __data_2015_05_check 
  CHECK(valid >= '2015-05-01 00:00+00'::timestamptz 
        and valid < '2015-06-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_05_grid_idx on data_2015_05(grid_idx);
CREATE INDEX data_2015_05_valid_idx on data_2015_05(valid);
GRANT SELECT on data_2015_05 to nobody,apache;


 create table data_2015_06( 
  CONSTRAINT __data_2015_06_check 
  CHECK(valid >= '2015-06-01 00:00+00'::timestamptz 
        and valid < '2015-07-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_06_grid_idx on data_2015_06(grid_idx);
CREATE INDEX data_2015_06_valid_idx on data_2015_06(valid);
GRANT SELECT on data_2015_06 to nobody,apache;


 create table data_2015_07( 
  CONSTRAINT __data_2015_07_check 
  CHECK(valid >= '2015-07-01 00:00+00'::timestamptz 
        and valid < '2015-08-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_07_grid_idx on data_2015_07(grid_idx);
CREATE INDEX data_2015_07_valid_idx on data_2015_07(valid);
GRANT SELECT on data_2015_07 to nobody,apache;


 create table data_2015_08( 
  CONSTRAINT __data_2015_08_check 
  CHECK(valid >= '2015-08-01 00:00+00'::timestamptz 
        and valid < '2015-09-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_08_grid_idx on data_2015_08(grid_idx);
CREATE INDEX data_2015_08_valid_idx on data_2015_08(valid);
GRANT SELECT on data_2015_08 to nobody,apache;


 create table data_2015_09( 
  CONSTRAINT __data_2015_09_check 
  CHECK(valid >= '2015-09-01 00:00+00'::timestamptz 
        and valid < '2015-10-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_09_grid_idx on data_2015_09(grid_idx);
CREATE INDEX data_2015_09_valid_idx on data_2015_09(valid);
GRANT SELECT on data_2015_09 to nobody,apache;


 create table data_2015_10( 
  CONSTRAINT __data_2015_10_check 
  CHECK(valid >= '2015-10-01 00:00+00'::timestamptz 
        and valid < '2015-11-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_10_grid_idx on data_2015_10(grid_idx);
CREATE INDEX data_2015_10_valid_idx on data_2015_10(valid);
GRANT SELECT on data_2015_10 to nobody,apache;


 create table data_2015_11( 
  CONSTRAINT __data_2015_11_check 
  CHECK(valid >= '2015-11-01 00:00+00'::timestamptz 
        and valid < '2015-12-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_11_grid_idx on data_2015_11(grid_idx);
CREATE INDEX data_2015_11_valid_idx on data_2015_11(valid);
GRANT SELECT on data_2015_11 to nobody,apache;


 create table data_2015_12( 
  CONSTRAINT __data_2015_12_check 
  CHECK(valid >= '2015-12-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2015_12_grid_idx on data_2015_12(grid_idx);
CREATE INDEX data_2015_12_valid_idx on data_2015_12(valid);
GRANT SELECT on data_2015_12 to nobody,apache;
 create table data_2016_01( 
  CONSTRAINT __data_2016_01_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2016-02-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_01_grid_idx on data_2016_01(grid_idx);
CREATE INDEX data_2016_01_valid_idx on data_2016_01(valid);
GRANT SELECT on data_2016_01 to nobody,apache;


 create table data_2016_02( 
  CONSTRAINT __data_2016_02_check 
  CHECK(valid >= '2016-02-01 00:00+00'::timestamptz 
        and valid < '2016-03-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_02_grid_idx on data_2016_02(grid_idx);
CREATE INDEX data_2016_02_valid_idx on data_2016_02(valid);
GRANT SELECT on data_2016_02 to nobody,apache;


 create table data_2016_03( 
  CONSTRAINT __data_2016_03_check 
  CHECK(valid >= '2016-03-01 00:00+00'::timestamptz 
        and valid < '2016-04-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_03_grid_idx on data_2016_03(grid_idx);
CREATE INDEX data_2016_03_valid_idx on data_2016_03(valid);
GRANT SELECT on data_2016_03 to nobody,apache;


 create table data_2016_04( 
  CONSTRAINT __data_2016_04_check 
  CHECK(valid >= '2016-04-01 00:00+00'::timestamptz 
        and valid < '2016-05-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_04_grid_idx on data_2016_04(grid_idx);
CREATE INDEX data_2016_04_valid_idx on data_2016_04(valid);
GRANT SELECT on data_2016_04 to nobody,apache;


 create table data_2016_05( 
  CONSTRAINT __data_2016_05_check 
  CHECK(valid >= '2016-05-01 00:00+00'::timestamptz 
        and valid < '2016-06-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_05_grid_idx on data_2016_05(grid_idx);
CREATE INDEX data_2016_05_valid_idx on data_2016_05(valid);
GRANT SELECT on data_2016_05 to nobody,apache;


 create table data_2016_06( 
  CONSTRAINT __data_2016_06_check 
  CHECK(valid >= '2016-06-01 00:00+00'::timestamptz 
        and valid < '2016-07-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_06_grid_idx on data_2016_06(grid_idx);
CREATE INDEX data_2016_06_valid_idx on data_2016_06(valid);
GRANT SELECT on data_2016_06 to nobody,apache;


 create table data_2016_07( 
  CONSTRAINT __data_2016_07_check 
  CHECK(valid >= '2016-07-01 00:00+00'::timestamptz 
        and valid < '2016-08-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_07_grid_idx on data_2016_07(grid_idx);
CREATE INDEX data_2016_07_valid_idx on data_2016_07(valid);
GRANT SELECT on data_2016_07 to nobody,apache;


 create table data_2016_08( 
  CONSTRAINT __data_2016_08_check 
  CHECK(valid >= '2016-08-01 00:00+00'::timestamptz 
        and valid < '2016-09-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_08_grid_idx on data_2016_08(grid_idx);
CREATE INDEX data_2016_08_valid_idx on data_2016_08(valid);
GRANT SELECT on data_2016_08 to nobody,apache;


 create table data_2016_09( 
  CONSTRAINT __data_2016_09_check 
  CHECK(valid >= '2016-09-01 00:00+00'::timestamptz 
        and valid < '2016-10-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_09_grid_idx on data_2016_09(grid_idx);
CREATE INDEX data_2016_09_valid_idx on data_2016_09(valid);
GRANT SELECT on data_2016_09 to nobody,apache;


 create table data_2016_10( 
  CONSTRAINT __data_2016_10_check 
  CHECK(valid >= '2016-10-01 00:00+00'::timestamptz 
        and valid < '2016-11-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_10_grid_idx on data_2016_10(grid_idx);
CREATE INDEX data_2016_10_valid_idx on data_2016_10(valid);
GRANT SELECT on data_2016_10 to nobody,apache;


 create table data_2016_11( 
  CONSTRAINT __data_2016_11_check 
  CHECK(valid >= '2016-11-01 00:00+00'::timestamptz 
        and valid < '2016-12-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_11_grid_idx on data_2016_11(grid_idx);
CREATE INDEX data_2016_11_valid_idx on data_2016_11(valid);
GRANT SELECT on data_2016_11 to nobody,apache;


 create table data_2016_12( 
  CONSTRAINT __data_2016_12_check 
  CHECK(valid >= '2016-12-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2016_12_grid_idx on data_2016_12(grid_idx);
CREATE INDEX data_2016_12_valid_idx on data_2016_12(valid);
GRANT SELECT on data_2016_12 to nobody,apache;

create table data_2017_01( 
  CONSTRAINT __data_2017_01_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2017-02-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_01_grid_idx on data_2017_01(grid_idx);
CREATE INDEX data_2017_01_valid_idx on data_2017_01(valid);
GRANT SELECT on data_2017_01 to nobody,apache;


 create table data_2017_02( 
  CONSTRAINT __data_2017_02_check 
  CHECK(valid >= '2017-02-01 00:00+00'::timestamptz 
        and valid < '2017-03-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_02_grid_idx on data_2017_02(grid_idx);
CREATE INDEX data_2017_02_valid_idx on data_2017_02(valid);
GRANT SELECT on data_2017_02 to nobody,apache;


 create table data_2017_03( 
  CONSTRAINT __data_2017_03_check 
  CHECK(valid >= '2017-03-01 00:00+00'::timestamptz 
        and valid < '2017-04-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_03_grid_idx on data_2017_03(grid_idx);
CREATE INDEX data_2017_03_valid_idx on data_2017_03(valid);
GRANT SELECT on data_2017_03 to nobody,apache;


 create table data_2017_04( 
  CONSTRAINT __data_2017_04_check 
  CHECK(valid >= '2017-04-01 00:00+00'::timestamptz 
        and valid < '2017-05-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_04_grid_idx on data_2017_04(grid_idx);
CREATE INDEX data_2017_04_valid_idx on data_2017_04(valid);
GRANT SELECT on data_2017_04 to nobody,apache;


 create table data_2017_05( 
  CONSTRAINT __data_2017_05_check 
  CHECK(valid >= '2017-05-01 00:00+00'::timestamptz 
        and valid < '2017-06-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_05_grid_idx on data_2017_05(grid_idx);
CREATE INDEX data_2017_05_valid_idx on data_2017_05(valid);
GRANT SELECT on data_2017_05 to nobody,apache;


 create table data_2017_06( 
  CONSTRAINT __data_2017_06_check 
  CHECK(valid >= '2017-06-01 00:00+00'::timestamptz 
        and valid < '2017-07-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_06_grid_idx on data_2017_06(grid_idx);
CREATE INDEX data_2017_06_valid_idx on data_2017_06(valid);
GRANT SELECT on data_2017_06 to nobody,apache;


 create table data_2017_07( 
  CONSTRAINT __data_2017_07_check 
  CHECK(valid >= '2017-07-01 00:00+00'::timestamptz 
        and valid < '2017-08-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_07_grid_idx on data_2017_07(grid_idx);
CREATE INDEX data_2017_07_valid_idx on data_2017_07(valid);
GRANT SELECT on data_2017_07 to nobody,apache;


 create table data_2017_08( 
  CONSTRAINT __data_2017_08_check 
  CHECK(valid >= '2017-08-01 00:00+00'::timestamptz 
        and valid < '2017-09-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_08_grid_idx on data_2017_08(grid_idx);
CREATE INDEX data_2017_08_valid_idx on data_2017_08(valid);
GRANT SELECT on data_2017_08 to nobody,apache;


 create table data_2017_09( 
  CONSTRAINT __data_2017_09_check 
  CHECK(valid >= '2017-09-01 00:00+00'::timestamptz 
        and valid < '2017-10-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_09_grid_idx on data_2017_09(grid_idx);
CREATE INDEX data_2017_09_valid_idx on data_2017_09(valid);
GRANT SELECT on data_2017_09 to nobody,apache;


 create table data_2017_10( 
  CONSTRAINT __data_2017_10_check 
  CHECK(valid >= '2017-10-01 00:00+00'::timestamptz 
        and valid < '2017-11-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_10_grid_idx on data_2017_10(grid_idx);
CREATE INDEX data_2017_10_valid_idx on data_2017_10(valid);
GRANT SELECT on data_2017_10 to nobody,apache;


 create table data_2017_11( 
  CONSTRAINT __data_2017_11_check 
  CHECK(valid >= '2017-11-01 00:00+00'::timestamptz 
        and valid < '2017-12-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_11_grid_idx on data_2017_11(grid_idx);
CREATE INDEX data_2017_11_valid_idx on data_2017_11(valid);
GRANT SELECT on data_2017_11 to nobody,apache;


 create table data_2017_12( 
  CONSTRAINT __data_2017_12_check 
  CHECK(valid >= '2017-12-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2017_12_grid_idx on data_2017_12(grid_idx);
CREATE INDEX data_2017_12_valid_idx on data_2017_12(valid);
GRANT SELECT on data_2017_12 to nobody,apache;

create table data_2018_01( 
  CONSTRAINT __data_2018_01_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2018-02-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_01_grid_idx on data_2018_01(grid_idx);
CREATE INDEX data_2018_01_valid_idx on data_2018_01(valid);
GRANT SELECT on data_2018_01 to nobody,apache;


 create table data_2018_02( 
  CONSTRAINT __data_2018_02_check 
  CHECK(valid >= '2018-02-01 00:00+00'::timestamptz 
        and valid < '2018-03-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_02_grid_idx on data_2018_02(grid_idx);
CREATE INDEX data_2018_02_valid_idx on data_2018_02(valid);
GRANT SELECT on data_2018_02 to nobody,apache;


 create table data_2018_03( 
  CONSTRAINT __data_2018_03_check 
  CHECK(valid >= '2018-03-01 00:00+00'::timestamptz 
        and valid < '2018-04-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_03_grid_idx on data_2018_03(grid_idx);
CREATE INDEX data_2018_03_valid_idx on data_2018_03(valid);
GRANT SELECT on data_2018_03 to nobody,apache;


 create table data_2018_04( 
  CONSTRAINT __data_2018_04_check 
  CHECK(valid >= '2018-04-01 00:00+00'::timestamptz 
        and valid < '2018-05-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_04_grid_idx on data_2018_04(grid_idx);
CREATE INDEX data_2018_04_valid_idx on data_2018_04(valid);
GRANT SELECT on data_2018_04 to nobody,apache;


 create table data_2018_05( 
  CONSTRAINT __data_2018_05_check 
  CHECK(valid >= '2018-05-01 00:00+00'::timestamptz 
        and valid < '2018-06-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_05_grid_idx on data_2018_05(grid_idx);
CREATE INDEX data_2018_05_valid_idx on data_2018_05(valid);
GRANT SELECT on data_2018_05 to nobody,apache;


 create table data_2018_06( 
  CONSTRAINT __data_2018_06_check 
  CHECK(valid >= '2018-06-01 00:00+00'::timestamptz 
        and valid < '2018-07-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_06_grid_idx on data_2018_06(grid_idx);
CREATE INDEX data_2018_06_valid_idx on data_2018_06(valid);
GRANT SELECT on data_2018_06 to nobody,apache;


 create table data_2018_07( 
  CONSTRAINT __data_2018_07_check 
  CHECK(valid >= '2018-07-01 00:00+00'::timestamptz 
        and valid < '2018-08-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_07_grid_idx on data_2018_07(grid_idx);
CREATE INDEX data_2018_07_valid_idx on data_2018_07(valid);
GRANT SELECT on data_2018_07 to nobody,apache;


 create table data_2018_08( 
  CONSTRAINT __data_2018_08_check 
  CHECK(valid >= '2018-08-01 00:00+00'::timestamptz 
        and valid < '2018-09-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_08_grid_idx on data_2018_08(grid_idx);
CREATE INDEX data_2018_08_valid_idx on data_2018_08(valid);
GRANT SELECT on data_2018_08 to nobody,apache;


 create table data_2018_09( 
  CONSTRAINT __data_2018_09_check 
  CHECK(valid >= '2018-09-01 00:00+00'::timestamptz 
        and valid < '2018-10-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_09_grid_idx on data_2018_09(grid_idx);
CREATE INDEX data_2018_09_valid_idx on data_2018_09(valid);
GRANT SELECT on data_2018_09 to nobody,apache;


 create table data_2018_10( 
  CONSTRAINT __data_2018_10_check 
  CHECK(valid >= '2018-10-01 00:00+00'::timestamptz 
        and valid < '2018-11-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_10_grid_idx on data_2018_10(grid_idx);
CREATE INDEX data_2018_10_valid_idx on data_2018_10(valid);
GRANT SELECT on data_2018_10 to nobody,apache;


 create table data_2018_11( 
  CONSTRAINT __data_2018_11_check 
  CHECK(valid >= '2018-11-01 00:00+00'::timestamptz 
        and valid < '2018-12-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_11_grid_idx on data_2018_11(grid_idx);
CREATE INDEX data_2018_11_valid_idx on data_2018_11(valid);
GRANT SELECT on data_2018_11 to nobody,apache;


 create table data_2018_12( 
  CONSTRAINT __data_2018_12_check 
  CHECK(valid >= '2018-12-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2018_12_grid_idx on data_2018_12(grid_idx);
CREATE INDEX data_2018_12_valid_idx on data_2018_12(valid);
GRANT SELECT on data_2018_12 to nobody,apache;

create table data_2019_01( 
  CONSTRAINT __data_2019_01_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2019-02-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_01_grid_idx on data_2019_01(grid_idx);
CREATE INDEX data_2019_01_valid_idx on data_2019_01(valid);
GRANT SELECT on data_2019_01 to nobody,apache;


 create table data_2019_02( 
  CONSTRAINT __data_2019_02_check 
  CHECK(valid >= '2019-02-01 00:00+00'::timestamptz 
        and valid < '2019-03-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_02_grid_idx on data_2019_02(grid_idx);
CREATE INDEX data_2019_02_valid_idx on data_2019_02(valid);
GRANT SELECT on data_2019_02 to nobody,apache;


 create table data_2019_03( 
  CONSTRAINT __data_2019_03_check 
  CHECK(valid >= '2019-03-01 00:00+00'::timestamptz 
        and valid < '2019-04-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_03_grid_idx on data_2019_03(grid_idx);
CREATE INDEX data_2019_03_valid_idx on data_2019_03(valid);
GRANT SELECT on data_2019_03 to nobody,apache;


 create table data_2019_04( 
  CONSTRAINT __data_2019_04_check 
  CHECK(valid >= '2019-04-01 00:00+00'::timestamptz 
        and valid < '2019-05-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_04_grid_idx on data_2019_04(grid_idx);
CREATE INDEX data_2019_04_valid_idx on data_2019_04(valid);
GRANT SELECT on data_2019_04 to nobody,apache;


 create table data_2019_05( 
  CONSTRAINT __data_2019_05_check 
  CHECK(valid >= '2019-05-01 00:00+00'::timestamptz 
        and valid < '2019-06-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_05_grid_idx on data_2019_05(grid_idx);
CREATE INDEX data_2019_05_valid_idx on data_2019_05(valid);
GRANT SELECT on data_2019_05 to nobody,apache;


 create table data_2019_06( 
  CONSTRAINT __data_2019_06_check 
  CHECK(valid >= '2019-06-01 00:00+00'::timestamptz 
        and valid < '2019-07-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_06_grid_idx on data_2019_06(grid_idx);
CREATE INDEX data_2019_06_valid_idx on data_2019_06(valid);
GRANT SELECT on data_2019_06 to nobody,apache;


 create table data_2019_07( 
  CONSTRAINT __data_2019_07_check 
  CHECK(valid >= '2019-07-01 00:00+00'::timestamptz 
        and valid < '2019-08-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_07_grid_idx on data_2019_07(grid_idx);
CREATE INDEX data_2019_07_valid_idx on data_2019_07(valid);
GRANT SELECT on data_2019_07 to nobody,apache;


 create table data_2019_08( 
  CONSTRAINT __data_2019_08_check 
  CHECK(valid >= '2019-08-01 00:00+00'::timestamptz 
        and valid < '2019-09-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_08_grid_idx on data_2019_08(grid_idx);
CREATE INDEX data_2019_08_valid_idx on data_2019_08(valid);
GRANT SELECT on data_2019_08 to nobody,apache;


 create table data_2019_09( 
  CONSTRAINT __data_2019_09_check 
  CHECK(valid >= '2019-09-01 00:00+00'::timestamptz 
        and valid < '2019-10-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_09_grid_idx on data_2019_09(grid_idx);
CREATE INDEX data_2019_09_valid_idx on data_2019_09(valid);
GRANT SELECT on data_2019_09 to nobody,apache;


 create table data_2019_10( 
  CONSTRAINT __data_2019_10_check 
  CHECK(valid >= '2019-10-01 00:00+00'::timestamptz 
        and valid < '2019-11-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_10_grid_idx on data_2019_10(grid_idx);
CREATE INDEX data_2019_10_valid_idx on data_2019_10(valid);
GRANT SELECT on data_2019_10 to nobody,apache;


 create table data_2019_11( 
  CONSTRAINT __data_2019_11_check 
  CHECK(valid >= '2019-11-01 00:00+00'::timestamptz 
        and valid < '2019-12-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_11_grid_idx on data_2019_11(grid_idx);
CREATE INDEX data_2019_11_valid_idx on data_2019_11(valid);
GRANT SELECT on data_2019_11 to nobody,apache;


 create table data_2019_12( 
  CONSTRAINT __data_2019_12_check 
  CHECK(valid >= '2019-12-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (data);
CREATE INDEX data_2019_12_grid_idx on data_2019_12(grid_idx);
CREATE INDEX data_2019_12_valid_idx on data_2019_12(valid);
GRANT SELECT on data_2019_12 to nobody,apache;
