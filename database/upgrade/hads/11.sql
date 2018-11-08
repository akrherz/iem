CREATE TABLE hml_forecast_data_2019(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2019_idx on
  hml_forecast_data_2019(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2019 to nobody,apache;

create table hml_observed_data_2019(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2019_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2019_idx on
        hml_observed_data_2019(station, valid);
GRANT SELECT on hml_observed_data_2019 to nobody,apache;

---
---
---
CREATE TABLE raw2019(
    station varchar(8),
    valid timestamptz,
    key varchar(11),
    value real
);
GRANT SELECT on raw2019 to nobody,apache;

create table raw2019_01( 
  CONSTRAINT __raw2019_01_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2019-02-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_01_idx on raw2019_01(station, valid);
CREATE INDEX raw2019_01_valid_idx on raw2019_01(valid);
grant select on raw2019_01 to nobody,apache;

create table raw2019_02( 
  CONSTRAINT __raw2019_02_check 
  CHECK(valid >= '2019-02-01 00:00+00'::timestamptz 
        and valid < '2019-03-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_02_idx on raw2019_02(station, valid);
CREATE INDEX raw2019_02_valid_idx on raw2019_02(valid);
grant select on raw2019_02 to nobody,apache;

create table raw2019_03( 
  CONSTRAINT __raw2019_03_check 
  CHECK(valid >= '2019-03-01 00:00+00'::timestamptz 
        and valid < '2019-04-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_03_idx on raw2019_03(station, valid);
CREATE INDEX raw2019_03_valid_idx on raw2019_03(valid);
grant select on raw2019_03 to nobody,apache;

create table raw2019_04( 
  CONSTRAINT __raw2019_04_check 
  CHECK(valid >= '2019-04-01 00:00+00'::timestamptz 
        and valid < '2019-05-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_04_idx on raw2019_04(station, valid);
CREATE INDEX raw2019_04_valid_idx on raw2019_04(valid);
grant select on raw2019_04 to nobody,apache;

create table raw2019_05( 
  CONSTRAINT __raw2019_05_check 
  CHECK(valid >= '2019-05-01 00:00+00'::timestamptz 
        and valid < '2019-06-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_05_idx on raw2019_05(station, valid);
CREATE INDEX raw2019_05_valid_idx on raw2019_05(valid);
grant select on raw2019_05 to nobody,apache;

create table raw2019_06( 
  CONSTRAINT __raw2019_06_check 
  CHECK(valid >= '2019-06-01 00:00+00'::timestamptz 
        and valid < '2019-07-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_06_idx on raw2019_06(station, valid);
CREATE INDEX raw2019_06_valid_idx on raw2019_06(valid);
grant select on raw2019_06 to nobody,apache;

create table raw2019_07( 
  CONSTRAINT __raw2019_07_check 
  CHECK(valid >= '2019-07-01 00:00+00'::timestamptz 
        and valid < '2019-08-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_07_idx on raw2019_07(station, valid);
CREATE INDEX raw2019_07_valid_idx on raw2019_07(valid);
grant select on raw2019_07 to nobody,apache;

create table raw2019_08( 
  CONSTRAINT __raw2019_08_check 
  CHECK(valid >= '2019-08-01 00:00+00'::timestamptz 
        and valid < '2019-09-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_08_idx on raw2019_08(station, valid);
CREATE INDEX raw2019_08_valid_idx on raw2019_08(valid);
grant select on raw2019_08 to nobody,apache;

create table raw2019_09( 
  CONSTRAINT __raw2019_09_check 
  CHECK(valid >= '2019-09-01 00:00+00'::timestamptz 
        and valid < '2019-10-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_09_idx on raw2019_09(station, valid);
CREATE INDEX raw2019_09_valid_idx on raw2019_09(valid);
grant select on raw2019_09 to nobody,apache;

create table raw2019_10( 
  CONSTRAINT __raw2019_10_check 
  CHECK(valid >= '2019-10-01 00:00+00'::timestamptz 
        and valid < '2019-11-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_10_idx on raw2019_10(station, valid);
CREATE INDEX raw2019_10_valid_idx on raw2019_10(valid);
grant select on raw2019_10 to nobody,apache;

create table raw2019_11( 
  CONSTRAINT __raw2019_11_check 
  CHECK(valid >= '2019-11-01 00:00+00'::timestamptz 
        and valid < '2019-12-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_11_idx on raw2019_11(station, valid);
CREATE INDEX raw2019_11_valid_idx on raw2019_11(valid);
grant select on raw2019_11 to nobody,apache;

create table raw2019_12( 
  CONSTRAINT __raw2019_12_check 
  CHECK(valid >= '2019-12-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (raw2019);
CREATE INDEX raw2019_12_idx on raw2019_12(station, valid);
CREATE INDEX raw2019_12_valid_idx on raw2019_12(valid);
grant select on raw2019_12 to nobody,apache;

create table t2019( 
  CONSTRAINT __t2019_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2019_idx on t2019(station, valid);
CREATE INDEX t2019_valid_idx on t2019(valid);
grant select on t2019 to nobody,apache;
