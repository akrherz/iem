-- Storage of HML forecasts
DROP TABLE IF EXISTS hml_forecast_data_2016;
DROP TABLE IF EXISTS hml_forecast;
CREATE TABLE hml_forecast(
  id SERIAL UNIQUE,
  station varchar(8),
  generationtime timestamptz,
  issued timestamptz,
  forecast_sts timestamptz,
  forecast_ets timestamptz,
  originator varchar(8),
  product_id varchar(32),
  primaryname varchar(64),
  primaryunits varchar(64),
  secondaryname varchar(64),
  secondaryunits varchar(64));
CREATE INDEX hml_forecast_idx on hml_forecast(station, generationtime);
GRANT SELECT on hml_forecast to nobody,apache;

CREATE TABLE hml_forecast_data_2016(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2016_idx on
  hml_forecast_data_2016(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2016 to nobody,apache;

CREATE TABLE hml_observed_keys(
  id smallint UNIQUE,
  label varchar(32));
GRANT SELECT on hml_observed_keys to nobody,apache;

INSERT into hml_observed_keys values
 (0, 'Depth Below Sfc[ft]'),
 (1, 'Discharge Velocity[mph]'),
 (2, 'Flow[kcfs]'),
 (3, 'Forebay Elevation[ft]'),
 (4, 'Generator Discharge[kcfs]'),
 (5, 'Inflow Discharge[kcfs]'),
 (6, 'Lake Elev Abv Datum[ft]'),
 (7, 'Lake Elevation[ft]'),
 (8, 'Pool[ft]'),
 (9, 'Precip[inches]'),
 (10, 'Reading Height - MSL[ft]'),
 (11, 'Reading Height - Sfc[ft]'),
 (12, 'River Discharge[kcfs]'),
 (13, 'Spillway Tailwater[ft]'),
 (14, 'Stage[ft]'),
 (15, 'Stage Trnd Indicator[code]'),
 (16, 'Tailwater[ft]'),
 (17, 'Tide Height[ft]'),
 (18, 'Total Discharge[kcfs]');


CREATE FUNCTION get_hml_observed_key(text)
RETURNS smallint
LANGUAGE sql
AS $_$
  SELECT id from hml_observed_keys where label = $1
$_$;

DROP TABLE IF EXISTS hml_observed_data_2016;
DROP TABLE IF EXISTS hml_observed_data;
CREATE TABLE hml_observed_data(
	station varchar(8),
	valid timestamptz,
	key smallint REFERENCES hml_observed_keys(id),
	value real);
GRANT SELECT on hml_observed_data to nobody,apache;

create table hml_observed_data_2016(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2016_check
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz
        and valid < '2017-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2016_idx on
	hml_observed_data_2016(station, valid);
GRANT SELECT on hml_observed_data_2016 to nobody,apache;
