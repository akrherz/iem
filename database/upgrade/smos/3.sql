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
