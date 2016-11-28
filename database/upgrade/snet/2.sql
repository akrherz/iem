create table t2017_01( 
  CONSTRAINT __t2017_01_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2017-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_01_station on t2017_01(station);
CREATE INDEX t2017_01_valid_idx on t2017_01(valid);
GRANT SELECT on t2017_01 to nobody,apache;


 create table t2017_02( 
  CONSTRAINT __t2017_02_check 
  CHECK(valid >= '2017-02-01 00:00+00'::timestamptz 
        and valid < '2017-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_02_station on t2017_02(station);
CREATE INDEX t2017_02_valid_idx on t2017_02(valid);
GRANT SELECT on t2017_02 to nobody,apache;


 create table t2017_03( 
  CONSTRAINT __t2017_03_check 
  CHECK(valid >= '2017-03-01 00:00+00'::timestamptz 
        and valid < '2017-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_03_station on t2017_03(station);
CREATE INDEX t2017_03_valid_idx on t2017_03(valid);
GRANT SELECT on t2017_03 to nobody,apache;


 create table t2017_04( 
  CONSTRAINT __t2017_04_check 
  CHECK(valid >= '2017-04-01 00:00+00'::timestamptz 
        and valid < '2017-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_04_station on t2017_04(station);
CREATE INDEX t2017_04_valid_idx on t2017_04(valid);
GRANT SELECT on t2017_04 to nobody,apache;


 create table t2017_05( 
  CONSTRAINT __t2017_05_check 
  CHECK(valid >= '2017-05-01 00:00+00'::timestamptz 
        and valid < '2017-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_05_station on t2017_05(station);
CREATE INDEX t2017_05_valid_idx on t2017_05(valid);
GRANT SELECT on t2017_05 to nobody,apache;


 create table t2017_06( 
  CONSTRAINT __t2017_06_check 
  CHECK(valid >= '2017-06-01 00:00+00'::timestamptz 
        and valid < '2017-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_06_station on t2017_06(station);
CREATE INDEX t2017_06_valid_idx on t2017_06(valid);
GRANT SELECT on t2017_06 to nobody,apache;


 create table t2017_07( 
  CONSTRAINT __t2017_07_check 
  CHECK(valid >= '2017-07-01 00:00+00'::timestamptz 
        and valid < '2017-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_07_station on t2017_07(station);
CREATE INDEX t2017_07_valid_idx on t2017_07(valid);
GRANT SELECT on t2017_07 to nobody,apache;


 create table t2017_08( 
  CONSTRAINT __t2017_08_check 
  CHECK(valid >= '2017-08-01 00:00+00'::timestamptz 
        and valid < '2017-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_08_station on t2017_08(station);
CREATE INDEX t2017_08_valid_idx on t2017_08(valid);
GRANT SELECT on t2017_08 to nobody,apache;


 create table t2017_09( 
  CONSTRAINT __t2017_09_check 
  CHECK(valid >= '2017-09-01 00:00+00'::timestamptz 
        and valid < '2017-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_09_station on t2017_09(station);
CREATE INDEX t2017_09_valid_idx on t2017_09(valid);
GRANT SELECT on t2017_09 to nobody,apache;


 create table t2017_10( 
  CONSTRAINT __t2017_10_check 
  CHECK(valid >= '2017-10-01 00:00+00'::timestamptz 
        and valid < '2017-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_10_station on t2017_10(station);
CREATE INDEX t2017_10_valid_idx on t2017_10(valid);
GRANT SELECT on t2017_10 to nobody,apache;


 create table t2017_11( 
  CONSTRAINT __t2017_11_check 
  CHECK(valid >= '2017-11-01 00:00+00'::timestamptz 
        and valid < '2017-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_11_station on t2017_11(station);
CREATE INDEX t2017_11_valid_idx on t2017_11(valid);
GRANT SELECT on t2017_11 to nobody,apache;


 create table t2017_12( 
  CONSTRAINT __t2017_12_check 
  CHECK(valid >= '2017-12-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2017_12_station on t2017_12(station);
CREATE INDEX t2017_12_valid_idx on t2017_12(valid);
GRANT SELECT on t2017_12 to nobody,apache;
