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
