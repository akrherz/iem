---
---
---
CREATE TABLE raw2016(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2016 to nobody,apache;

create table raw2016_01( 
  CONSTRAINT __raw2016_01_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2016-02-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_01_idx on raw2016_01(station, valid);
CREATE INDEX raw2016_01_valid_idx on raw2016_01(valid);
grant select on raw2016_01 to nobody,apache;

create table raw2016_02( 
  CONSTRAINT __raw2016_02_check 
  CHECK(valid >= '2016-02-01 00:00+00'::timestamptz 
        and valid < '2016-03-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_02_idx on raw2016_02(station, valid);
CREATE INDEX raw2016_02_valid_idx on raw2016_02(valid);
grant select on raw2016_02 to nobody,apache;

create table raw2016_03( 
  CONSTRAINT __raw2016_03_check 
  CHECK(valid >= '2016-03-01 00:00+00'::timestamptz 
        and valid < '2016-04-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_03_idx on raw2016_03(station, valid);
CREATE INDEX raw2016_03_valid_idx on raw2016_03(valid);
grant select on raw2016_03 to nobody,apache;

create table raw2016_04( 
  CONSTRAINT __raw2016_04_check 
  CHECK(valid >= '2016-04-01 00:00+00'::timestamptz 
        and valid < '2016-05-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_04_idx on raw2016_04(station, valid);
CREATE INDEX raw2016_04_valid_idx on raw2016_04(valid);
grant select on raw2016_04 to nobody,apache;

create table raw2016_05( 
  CONSTRAINT __raw2016_05_check 
  CHECK(valid >= '2016-05-01 00:00+00'::timestamptz 
        and valid < '2016-06-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_05_idx on raw2016_05(station, valid);
CREATE INDEX raw2016_05_valid_idx on raw2016_05(valid);
grant select on raw2016_05 to nobody,apache;

create table raw2016_06( 
  CONSTRAINT __raw2016_06_check 
  CHECK(valid >= '2016-06-01 00:00+00'::timestamptz 
        and valid < '2016-07-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_06_idx on raw2016_06(station, valid);
CREATE INDEX raw2016_06_valid_idx on raw2016_06(valid);
grant select on raw2016_06 to nobody,apache;

create table raw2016_07( 
  CONSTRAINT __raw2016_07_check 
  CHECK(valid >= '2016-07-01 00:00+00'::timestamptz 
        and valid < '2016-08-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_07_idx on raw2016_07(station, valid);
CREATE INDEX raw2016_07_valid_idx on raw2016_07(valid);
grant select on raw2016_07 to nobody,apache;

create table raw2016_08( 
  CONSTRAINT __raw2016_08_check 
  CHECK(valid >= '2016-08-01 00:00+00'::timestamptz 
        and valid < '2016-09-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_08_idx on raw2016_08(station, valid);
CREATE INDEX raw2016_08_valid_idx on raw2016_08(valid);
grant select on raw2016_08 to nobody,apache;

create table raw2016_09( 
  CONSTRAINT __raw2016_09_check 
  CHECK(valid >= '2016-09-01 00:00+00'::timestamptz 
        and valid < '2016-10-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_09_idx on raw2016_09(station, valid);
CREATE INDEX raw2016_09_valid_idx on raw2016_09(valid);
grant select on raw2016_09 to nobody,apache;

create table raw2016_10( 
  CONSTRAINT __raw2016_10_check 
  CHECK(valid >= '2016-10-01 00:00+00'::timestamptz 
        and valid < '2016-11-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_10_idx on raw2016_10(station, valid);
CREATE INDEX raw2016_10_valid_idx on raw2016_10(valid);
grant select on raw2016_10 to nobody,apache;

create table raw2016_11( 
  CONSTRAINT __raw2016_11_check 
  CHECK(valid >= '2016-11-01 00:00+00'::timestamptz 
        and valid < '2016-12-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_11_idx on raw2016_11(station, valid);
CREATE INDEX raw2016_11_valid_idx on raw2016_11(valid);
grant select on raw2016_11 to nobody,apache;

create table raw2016_12( 
  CONSTRAINT __raw2016_12_check 
  CHECK(valid >= '2016-12-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (raw2016);
CREATE INDEX raw2016_12_idx on raw2016_12(station, valid);
CREATE INDEX raw2016_12_valid_idx on raw2016_12(valid);
grant select on raw2016_12 to nobody,apache;
