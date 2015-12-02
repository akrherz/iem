CREATE TABLE monthly_rainfall_2016() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2016 to nobody,apache;
ALTER TABLE monthly_rainfall_2016 add constraint __monthly_rainfall_2016__constraint
  CHECK(valid >= '2016-01-01'::date and valid < '2017-01-01'::date);

CREATE TABLE daily_rainfall_2016() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2016 to nobody,apache;
ALTER TABLE daily_rainfall_2016 add constraint __daily_rainfall_2016__constraint
  CHECK(valid >= '2016-01-01'::date and valid < '2017-01-01'::date);
CREATE INDEX daily_rainfall_2016_hrap_i_idx on
  daily_rainfall_2016(hrap_i);
CREATE INDEX daily_rainfall_2016_valid_idx on
  daily_rainfall_2016(valid);
