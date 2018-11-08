create table t2019_01( 
  CONSTRAINT __t2019_01_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2019-02-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_01_station on t2019_01(station);
CREATE INDEX t2019_01_valid_idx on t2019_01(valid);
GRANT SELECT on t2019_01 to nobody,apache;


 create table t2019_02( 
  CONSTRAINT __t2019_02_check 
  CHECK(valid >= '2019-02-01 00:00+00'::timestamptz 
        and valid < '2019-03-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_02_station on t2019_02(station);
CREATE INDEX t2019_02_valid_idx on t2019_02(valid);
GRANT SELECT on t2019_02 to nobody,apache;


 create table t2019_03( 
  CONSTRAINT __t2019_03_check 
  CHECK(valid >= '2019-03-01 00:00+00'::timestamptz 
        and valid < '2019-04-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_03_station on t2019_03(station);
CREATE INDEX t2019_03_valid_idx on t2019_03(valid);
GRANT SELECT on t2019_03 to nobody,apache;


 create table t2019_04( 
  CONSTRAINT __t2019_04_check 
  CHECK(valid >= '2019-04-01 00:00+00'::timestamptz 
        and valid < '2019-05-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_04_station on t2019_04(station);
CREATE INDEX t2019_04_valid_idx on t2019_04(valid);
GRANT SELECT on t2019_04 to nobody,apache;


 create table t2019_05( 
  CONSTRAINT __t2019_05_check 
  CHECK(valid >= '2019-05-01 00:00+00'::timestamptz 
        and valid < '2019-06-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_05_station on t2019_05(station);
CREATE INDEX t2019_05_valid_idx on t2019_05(valid);
GRANT SELECT on t2019_05 to nobody,apache;


 create table t2019_06( 
  CONSTRAINT __t2019_06_check 
  CHECK(valid >= '2019-06-01 00:00+00'::timestamptz 
        and valid < '2019-07-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_06_station on t2019_06(station);
CREATE INDEX t2019_06_valid_idx on t2019_06(valid);
GRANT SELECT on t2019_06 to nobody,apache;


 create table t2019_07( 
  CONSTRAINT __t2019_07_check 
  CHECK(valid >= '2019-07-01 00:00+00'::timestamptz 
        and valid < '2019-08-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_07_station on t2019_07(station);
CREATE INDEX t2019_07_valid_idx on t2019_07(valid);
GRANT SELECT on t2019_07 to nobody,apache;


 create table t2019_08( 
  CONSTRAINT __t2019_08_check 
  CHECK(valid >= '2019-08-01 00:00+00'::timestamptz 
        and valid < '2019-09-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_08_station on t2019_08(station);
CREATE INDEX t2019_08_valid_idx on t2019_08(valid);
GRANT SELECT on t2019_08 to nobody,apache;


 create table t2019_09( 
  CONSTRAINT __t2019_09_check 
  CHECK(valid >= '2019-09-01 00:00+00'::timestamptz 
        and valid < '2019-10-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_09_station on t2019_09(station);
CREATE INDEX t2019_09_valid_idx on t2019_09(valid);
GRANT SELECT on t2019_09 to nobody,apache;


 create table t2019_10( 
  CONSTRAINT __t2019_10_check 
  CHECK(valid >= '2019-10-01 00:00+00'::timestamptz 
        and valid < '2019-11-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_10_station on t2019_10(station);
CREATE INDEX t2019_10_valid_idx on t2019_10(valid);
GRANT SELECT on t2019_10 to nobody,apache;


 create table t2019_11( 
  CONSTRAINT __t2019_11_check 
  CHECK(valid >= '2019-11-01 00:00+00'::timestamptz 
        and valid < '2019-12-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_11_station on t2019_11(station);
CREATE INDEX t2019_11_valid_idx on t2019_11(valid);
GRANT SELECT on t2019_11 to nobody,apache;


 create table t2019_12( 
  CONSTRAINT __t2019_12_check 
  CHECK(valid >= '2019-12-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_12_station on t2019_12(station);
CREATE INDEX t2019_12_valid_idx on t2019_12(valid);
GRANT SELECT on t2019_12 to nobody,apache;