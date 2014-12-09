CREATE TABLE monthly_rainfall_2015() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2015 to nobody,apache;
ALTER TABLE monthly_rainfall_2015 add constraint __monthly_rainfall_2015__constraint
  CHECK(valid >= '2015-01-01'::date and valid < '2016-01-01'::date);

CREATE TABLE daily_rainfall_2015() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2015 to nobody,apache;
ALTER TABLE daily_rainfall_2015 add constraint __daily_rainfall_2015__constraint
  CHECK(valid >= '2015-01-01'::date and valid < '2016-01-01'::date);
CREATE INDEX daily_rainfall_2015_hrap_i_idx on
  daily_rainfall_2015(hrap_i);
CREATE INDEX daily_rainfall_2015_valid_idx on
  daily_rainfall_2015(valid);
