create table t2016_01( 
  CONSTRAINT __t2016_01_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2016-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_01_station on t2016_01(station);
CREATE INDEX t2016_01_valid_idx on t2016_01(valid);
GRANT SELECT on t2016_01 to nobody,apache;


 create table t2016_02( 
  CONSTRAINT __t2016_02_check 
  CHECK(valid >= '2016-02-01 00:00+00'::timestamptz 
        and valid < '2016-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_02_station on t2016_02(station);
CREATE INDEX t2016_02_valid_idx on t2016_02(valid);
GRANT SELECT on t2016_02 to nobody,apache;


 create table t2016_03( 
  CONSTRAINT __t2016_03_check 
  CHECK(valid >= '2016-03-01 00:00+00'::timestamptz 
        and valid < '2016-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_03_station on t2016_03(station);
CREATE INDEX t2016_03_valid_idx on t2016_03(valid);
GRANT SELECT on t2016_03 to nobody,apache;


 create table t2016_04( 
  CONSTRAINT __t2016_04_check 
  CHECK(valid >= '2016-04-01 00:00+00'::timestamptz 
        and valid < '2016-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_04_station on t2016_04(station);
CREATE INDEX t2016_04_valid_idx on t2016_04(valid);
GRANT SELECT on t2016_04 to nobody,apache;


 create table t2016_05( 
  CONSTRAINT __t2016_05_check 
  CHECK(valid >= '2016-05-01 00:00+00'::timestamptz 
        and valid < '2016-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_05_station on t2016_05(station);
CREATE INDEX t2016_05_valid_idx on t2016_05(valid);
GRANT SELECT on t2016_05 to nobody,apache;


 create table t2016_06( 
  CONSTRAINT __t2016_06_check 
  CHECK(valid >= '2016-06-01 00:00+00'::timestamptz 
        and valid < '2016-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_06_station on t2016_06(station);
CREATE INDEX t2016_06_valid_idx on t2016_06(valid);
GRANT SELECT on t2016_06 to nobody,apache;


 create table t2016_07( 
  CONSTRAINT __t2016_07_check 
  CHECK(valid >= '2016-07-01 00:00+00'::timestamptz 
        and valid < '2016-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_07_station on t2016_07(station);
CREATE INDEX t2016_07_valid_idx on t2016_07(valid);
GRANT SELECT on t2016_07 to nobody,apache;


 create table t2016_08( 
  CONSTRAINT __t2016_08_check 
  CHECK(valid >= '2016-08-01 00:00+00'::timestamptz 
        and valid < '2016-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_08_station on t2016_08(station);
CREATE INDEX t2016_08_valid_idx on t2016_08(valid);
GRANT SELECT on t2016_08 to nobody,apache;


 create table t2016_09( 
  CONSTRAINT __t2016_09_check 
  CHECK(valid >= '2016-09-01 00:00+00'::timestamptz 
        and valid < '2016-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_09_station on t2016_09(station);
CREATE INDEX t2016_09_valid_idx on t2016_09(valid);
GRANT SELECT on t2016_09 to nobody,apache;


 create table t2016_10( 
  CONSTRAINT __t2016_10_check 
  CHECK(valid >= '2016-10-01 00:00+00'::timestamptz 
        and valid < '2016-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_10_station on t2016_10(station);
CREATE INDEX t2016_10_valid_idx on t2016_10(valid);
GRANT SELECT on t2016_10 to nobody,apache;


 create table t2016_11( 
  CONSTRAINT __t2016_11_check 
  CHECK(valid >= '2016-11-01 00:00+00'::timestamptz 
        and valid < '2016-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_11_station on t2016_11(station);
CREATE INDEX t2016_11_valid_idx on t2016_11(valid);
GRANT SELECT on t2016_11 to nobody,apache;


 create table t2016_12( 
  CONSTRAINT __t2016_12_check 
  CHECK(valid >= '2016-12-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_12_station on t2016_12(station);
CREATE INDEX t2016_12_valid_idx on t2016_12(valid);
GRANT SELECT on t2016_12 to nobody,apache;
