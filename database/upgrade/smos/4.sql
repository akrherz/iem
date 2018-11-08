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
