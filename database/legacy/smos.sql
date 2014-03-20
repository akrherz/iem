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
 
 CREATE TABLE data_2011_02() inherits (data);
 
 
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