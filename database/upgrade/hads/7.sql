---
---
---
CREATE TABLE raw2017(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
GRANT SELECT on raw2017 to nobody,apache;

create table raw2017_01( 
  CONSTRAINT __raw2017_01_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2017-02-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_01_idx on raw2017_01(station, valid);
CREATE INDEX raw2017_01_valid_idx on raw2017_01(valid);
grant select on raw2017_01 to nobody,apache;

create table raw2017_02( 
  CONSTRAINT __raw2017_02_check 
  CHECK(valid >= '2017-02-01 00:00+00'::timestamptz 
        and valid < '2017-03-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_02_idx on raw2017_02(station, valid);
CREATE INDEX raw2017_02_valid_idx on raw2017_02(valid);
grant select on raw2017_02 to nobody,apache;

create table raw2017_03( 
  CONSTRAINT __raw2017_03_check 
  CHECK(valid >= '2017-03-01 00:00+00'::timestamptz 
        and valid < '2017-04-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_03_idx on raw2017_03(station, valid);
CREATE INDEX raw2017_03_valid_idx on raw2017_03(valid);
grant select on raw2017_03 to nobody,apache;

create table raw2017_04( 
  CONSTRAINT __raw2017_04_check 
  CHECK(valid >= '2017-04-01 00:00+00'::timestamptz 
        and valid < '2017-05-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_04_idx on raw2017_04(station, valid);
CREATE INDEX raw2017_04_valid_idx on raw2017_04(valid);
grant select on raw2017_04 to nobody,apache;

create table raw2017_05( 
  CONSTRAINT __raw2017_05_check 
  CHECK(valid >= '2017-05-01 00:00+00'::timestamptz 
        and valid < '2017-06-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_05_idx on raw2017_05(station, valid);
CREATE INDEX raw2017_05_valid_idx on raw2017_05(valid);
grant select on raw2017_05 to nobody,apache;

create table raw2017_06( 
  CONSTRAINT __raw2017_06_check 
  CHECK(valid >= '2017-06-01 00:00+00'::timestamptz 
        and valid < '2017-07-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_06_idx on raw2017_06(station, valid);
CREATE INDEX raw2017_06_valid_idx on raw2017_06(valid);
grant select on raw2017_06 to nobody,apache;

create table raw2017_07( 
  CONSTRAINT __raw2017_07_check 
  CHECK(valid >= '2017-07-01 00:00+00'::timestamptz 
        and valid < '2017-08-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_07_idx on raw2017_07(station, valid);
CREATE INDEX raw2017_07_valid_idx on raw2017_07(valid);
grant select on raw2017_07 to nobody,apache;

create table raw2017_08( 
  CONSTRAINT __raw2017_08_check 
  CHECK(valid >= '2017-08-01 00:00+00'::timestamptz 
        and valid < '2017-09-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_08_idx on raw2017_08(station, valid);
CREATE INDEX raw2017_08_valid_idx on raw2017_08(valid);
grant select on raw2017_08 to nobody,apache;

create table raw2017_09( 
  CONSTRAINT __raw2017_09_check 
  CHECK(valid >= '2017-09-01 00:00+00'::timestamptz 
        and valid < '2017-10-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_09_idx on raw2017_09(station, valid);
CREATE INDEX raw2017_09_valid_idx on raw2017_09(valid);
grant select on raw2017_09 to nobody,apache;

create table raw2017_10( 
  CONSTRAINT __raw2017_10_check 
  CHECK(valid >= '2017-10-01 00:00+00'::timestamptz 
        and valid < '2017-11-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_10_idx on raw2017_10(station, valid);
CREATE INDEX raw2017_10_valid_idx on raw2017_10(valid);
grant select on raw2017_10 to nobody,apache;

create table raw2017_11( 
  CONSTRAINT __raw2017_11_check 
  CHECK(valid >= '2017-11-01 00:00+00'::timestamptz 
        and valid < '2017-12-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_11_idx on raw2017_11(station, valid);
CREATE INDEX raw2017_11_valid_idx on raw2017_11(valid);
grant select on raw2017_11 to nobody,apache;

create table raw2017_12( 
  CONSTRAINT __raw2017_12_check 
  CHECK(valid >= '2017-12-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (raw2017);
CREATE INDEX raw2017_12_idx on raw2017_12(station, valid);
CREATE INDEX raw2017_12_valid_idx on raw2017_12(valid);
grant select on raw2017_12 to nobody,apache;


CREATE TABLE hml_forecast_data_2017(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2017_idx on
  hml_forecast_data_2017(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2017 to nobody,apache;

create table hml_observed_data_2017(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2017_check
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
        and valid < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2017_idx on
        hml_observed_data_2017(station, valid);
GRANT SELECT on hml_observed_data_2017 to nobody,apache;
