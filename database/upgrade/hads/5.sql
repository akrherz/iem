-- Add older table
CREATE TABLE hml_forecast_data_2014(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2014_idx on
  hml_forecast_data_2014(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2014 to nobody,apache;

CREATE TABLE hml_forecast_data_2015(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2015_idx on
  hml_forecast_data_2015(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2015 to nobody,apache;

create table hml_observed_data_2014(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2014_check
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz
        and valid < '2015-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2014_idx on
	hml_observed_data_2014(station, valid);
GRANT SELECT on hml_observed_data_2014 to nobody,apache;

create table hml_observed_data_2015(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2015_check
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz
        and valid < '2016-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2015_idx on
	hml_observed_data_2015(station, valid);
GRANT SELECT on hml_observed_data_2015 to nobody,apache;
