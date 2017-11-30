CREATE TABLE hml_forecast_data_2018(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2018_idx on
  hml_forecast_data_2018(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2018 to nobody,apache;

create table hml_observed_data_2018(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2018_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2018_idx on
        hml_observed_data_2018(station, valid);
GRANT SELECT on hml_observed_data_2018 to nobody,apache;

---
---
---
CREATE TABLE raw2018(
    station varchar(8),
    valid timestamptz,
    key varchar(11),
    value real
);
GRANT SELECT on raw2018 to nobody,apache;

create table raw2018_01( 
  CONSTRAINT __raw2018_01_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2018-02-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_01_idx on raw2018_01(station, valid);
CREATE INDEX raw2018_01_valid_idx on raw2018_01(valid);
grant select on raw2018_01 to nobody,apache;

create table raw2018_02( 
  CONSTRAINT __raw2018_02_check 
  CHECK(valid >= '2018-02-01 00:00+00'::timestamptz 
        and valid < '2018-03-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_02_idx on raw2018_02(station, valid);
CREATE INDEX raw2018_02_valid_idx on raw2018_02(valid);
grant select on raw2018_02 to nobody,apache;

create table raw2018_03( 
  CONSTRAINT __raw2018_03_check 
  CHECK(valid >= '2018-03-01 00:00+00'::timestamptz 
        and valid < '2018-04-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_03_idx on raw2018_03(station, valid);
CREATE INDEX raw2018_03_valid_idx on raw2018_03(valid);
grant select on raw2018_03 to nobody,apache;

create table raw2018_04( 
  CONSTRAINT __raw2018_04_check 
  CHECK(valid >= '2018-04-01 00:00+00'::timestamptz 
        and valid < '2018-05-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_04_idx on raw2018_04(station, valid);
CREATE INDEX raw2018_04_valid_idx on raw2018_04(valid);
grant select on raw2018_04 to nobody,apache;

create table raw2018_05( 
  CONSTRAINT __raw2018_05_check 
  CHECK(valid >= '2018-05-01 00:00+00'::timestamptz 
        and valid < '2018-06-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_05_idx on raw2018_05(station, valid);
CREATE INDEX raw2018_05_valid_idx on raw2018_05(valid);
grant select on raw2018_05 to nobody,apache;

create table raw2018_06( 
  CONSTRAINT __raw2018_06_check 
  CHECK(valid >= '2018-06-01 00:00+00'::timestamptz 
        and valid < '2018-07-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_06_idx on raw2018_06(station, valid);
CREATE INDEX raw2018_06_valid_idx on raw2018_06(valid);
grant select on raw2018_06 to nobody,apache;

create table raw2018_07( 
  CONSTRAINT __raw2018_07_check 
  CHECK(valid >= '2018-07-01 00:00+00'::timestamptz 
        and valid < '2018-08-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_07_idx on raw2018_07(station, valid);
CREATE INDEX raw2018_07_valid_idx on raw2018_07(valid);
grant select on raw2018_07 to nobody,apache;

create table raw2018_08( 
  CONSTRAINT __raw2018_08_check 
  CHECK(valid >= '2018-08-01 00:00+00'::timestamptz 
        and valid < '2018-09-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_08_idx on raw2018_08(station, valid);
CREATE INDEX raw2018_08_valid_idx on raw2018_08(valid);
grant select on raw2018_08 to nobody,apache;

create table raw2018_09( 
  CONSTRAINT __raw2018_09_check 
  CHECK(valid >= '2018-09-01 00:00+00'::timestamptz 
        and valid < '2018-10-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_09_idx on raw2018_09(station, valid);
CREATE INDEX raw2018_09_valid_idx on raw2018_09(valid);
grant select on raw2018_09 to nobody,apache;

create table raw2018_10( 
  CONSTRAINT __raw2018_10_check 
  CHECK(valid >= '2018-10-01 00:00+00'::timestamptz 
        and valid < '2018-11-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_10_idx on raw2018_10(station, valid);
CREATE INDEX raw2018_10_valid_idx on raw2018_10(valid);
grant select on raw2018_10 to nobody,apache;

create table raw2018_11( 
  CONSTRAINT __raw2018_11_check 
  CHECK(valid >= '2018-11-01 00:00+00'::timestamptz 
        and valid < '2018-12-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_11_idx on raw2018_11(station, valid);
CREATE INDEX raw2018_11_valid_idx on raw2018_11(valid);
grant select on raw2018_11 to nobody,apache;

create table raw2018_12( 
  CONSTRAINT __raw2018_12_check 
  CHECK(valid >= '2018-12-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (raw2018);
CREATE INDEX raw2018_12_idx on raw2018_12(station, valid);
CREATE INDEX raw2018_12_valid_idx on raw2018_12(valid);
grant select on raw2018_12 to nobody,apache;

create table t2018( 
  CONSTRAINT __t2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2018_idx on t2018(station, valid);
CREATE INDEX t2018_valid_idx on t2018(valid);
grant select on t2018 to nobody,apache;
