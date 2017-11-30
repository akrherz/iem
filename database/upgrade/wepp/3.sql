CREATE TABLE daily_rainfall_2018() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2018 to nobody,apache;
ALTER TABLE daily_rainfall_2018 add constraint __daily_rainfall_2018__constraint
  CHECK(valid >= '2018-01-01'::date and valid < '2019-01-01'::date);
CREATE INDEX daily_rainfall_2018_hrap_i_idx on
  daily_rainfall_2018(hrap_i);
CREATE INDEX daily_rainfall_2018_valid_idx on
  daily_rainfall_2018(valid);
  