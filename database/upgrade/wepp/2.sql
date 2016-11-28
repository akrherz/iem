CREATE TABLE monthly_rainfall_2017() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2017 to nobody,apache;
ALTER TABLE monthly_rainfall_2017 add constraint __monthly_rainfall_2017__constraint
  CHECK(valid >= '2017-01-01'::date and valid < '2018-01-01'::date);

CREATE TABLE daily_rainfall_2017() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2017 to nobody,apache;
ALTER TABLE daily_rainfall_2017 add constraint __daily_rainfall_2017__constraint
  CHECK(valid >= '2017-01-01'::date and valid < '2018-01-01'::date);
CREATE INDEX daily_rainfall_2017_hrap_i_idx on
  daily_rainfall_2017(hrap_i);
CREATE INDEX daily_rainfall_2017_valid_idx on
  daily_rainfall_2017(valid);
