--
CREATE TABLE hml_forecast_data_2012(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2012_idx on
  hml_forecast_data_2012(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2012 to nobody,apache;

CREATE TABLE hml_forecast_data_2013(
  hml_forecast_id int REFERENCES hml_forecast(id),
  valid timestamptz,
  primary_value real,
  secondary_value real);
CREATE INDEX hml_forecast_data_2013_idx on
  hml_forecast_data_2013(hml_forecast_id);
GRANT SELECT on hml_forecast_data_2013 to nobody,apache;

create table hml_observed_data_2012(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2012_check
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz
        and valid < '2013-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2012_idx on
	hml_observed_data_2012(station, valid);
GRANT SELECT on hml_observed_data_2012 to nobody,apache;

create table hml_observed_data_2013(
  key smallint REFERENCES hml_observed_keys(id),
  CONSTRAINT __hml_observed_data_2013_check
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz
        and valid < '2014-01-01 00:00+00'::timestamptz))
  INHERITS (hml_observed_data);
CREATE INDEX hml_observed_data_2013_idx on
	hml_observed_data_2013(station, valid);
GRANT SELECT on hml_observed_data_2013 to nobody,apache;

CREATE INDEX hml_forecast_issued_idx on hml_forecast(issued);
