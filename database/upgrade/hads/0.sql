---
---
---
CREATE TABLE raw2015(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2015 to nobody,apache;

create table raw2015_01( 
  CONSTRAINT __raw2015_01_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2015-02-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_01_idx on raw2015_01(station, valid);
CREATE INDEX raw2015_01_valid_idx on raw2015_01(valid);
grant select on raw2015_01 to nobody,apache;

create table raw2015_02( 
  CONSTRAINT __raw2015_02_check 
  CHECK(valid >= '2015-02-01 00:00+00'::timestamptz 
        and valid < '2015-03-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_02_idx on raw2015_02(station, valid);
CREATE INDEX raw2015_02_valid_idx on raw2015_02(valid);
grant select on raw2015_02 to nobody,apache;

create table raw2015_03( 
  CONSTRAINT __raw2015_03_check 
  CHECK(valid >= '2015-03-01 00:00+00'::timestamptz 
        and valid < '2015-04-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_03_idx on raw2015_03(station, valid);
CREATE INDEX raw2015_03_valid_idx on raw2015_03(valid);
grant select on raw2015_03 to nobody,apache;

create table raw2015_04( 
  CONSTRAINT __raw2015_04_check 
  CHECK(valid >= '2015-04-01 00:00+00'::timestamptz 
        and valid < '2015-05-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_04_idx on raw2015_04(station, valid);
CREATE INDEX raw2015_04_valid_idx on raw2015_04(valid);
grant select on raw2015_04 to nobody,apache;

create table raw2015_05( 
  CONSTRAINT __raw2015_05_check 
  CHECK(valid >= '2015-05-01 00:00+00'::timestamptz 
        and valid < '2015-06-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_05_idx on raw2015_05(station, valid);
CREATE INDEX raw2015_05_valid_idx on raw2015_05(valid);
grant select on raw2015_05 to nobody,apache;

create table raw2015_06( 
  CONSTRAINT __raw2015_06_check 
  CHECK(valid >= '2015-06-01 00:00+00'::timestamptz 
        and valid < '2015-07-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_06_idx on raw2015_06(station, valid);
CREATE INDEX raw2015_06_valid_idx on raw2015_06(valid);
grant select on raw2015_06 to nobody,apache;

create table raw2015_07( 
  CONSTRAINT __raw2015_07_check 
  CHECK(valid >= '2015-07-01 00:00+00'::timestamptz 
        and valid < '2015-08-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_07_idx on raw2015_07(station, valid);
CREATE INDEX raw2015_07_valid_idx on raw2015_07(valid);
grant select on raw2015_07 to nobody,apache;

create table raw2015_08( 
  CONSTRAINT __raw2015_08_check 
  CHECK(valid >= '2015-08-01 00:00+00'::timestamptz 
        and valid < '2015-09-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_08_idx on raw2015_08(station, valid);
CREATE INDEX raw2015_08_valid_idx on raw2015_08(valid);
grant select on raw2015_08 to nobody,apache;

create table raw2015_09( 
  CONSTRAINT __raw2015_09_check 
  CHECK(valid >= '2015-09-01 00:00+00'::timestamptz 
        and valid < '2015-10-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_09_idx on raw2015_09(station, valid);
CREATE INDEX raw2015_09_valid_idx on raw2015_09(valid);
grant select on raw2015_09 to nobody,apache;

create table raw2015_10( 
  CONSTRAINT __raw2015_10_check 
  CHECK(valid >= '2015-10-01 00:00+00'::timestamptz 
        and valid < '2015-11-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_10_idx on raw2015_10(station, valid);
CREATE INDEX raw2015_10_valid_idx on raw2015_10(valid);
grant select on raw2015_10 to nobody,apache;

create table raw2015_11( 
  CONSTRAINT __raw2015_11_check 
  CHECK(valid >= '2015-11-01 00:00+00'::timestamptz 
        and valid < '2015-12-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_11_idx on raw2015_11(station, valid);
CREATE INDEX raw2015_11_valid_idx on raw2015_11(valid);
grant select on raw2015_11 to nobody,apache;

create table raw2015_12( 
  CONSTRAINT __raw2015_12_check 
  CHECK(valid >= '2015-12-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (raw2015);
CREATE INDEX raw2015_12_idx on raw2015_12(station, valid);
CREATE INDEX raw2015_12_valid_idx on raw2015_12(valid);
grant select on raw2015_12 to nobody,apache;
