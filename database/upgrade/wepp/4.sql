CREATE TABLE monthly_rainfall_2019() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2019 to nobody,apache;
ALTER TABLE monthly_rainfall_2019 add constraint __monthly_rainfall_2019__constraint
  CHECK(valid >= '2019-01-01'::date and valid < '2020-01-01'::date);

CREATE TABLE daily_rainfall_2019() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2019 to nobody,apache;
ALTER TABLE daily_rainfall_2019 add constraint __daily_rainfall_2019__constraint
  CHECK(valid >= '2019-01-01'::date and valid < '2020-01-01'::date);
CREATE INDEX daily_rainfall_2019_hrap_i_idx on
  daily_rainfall_2019(hrap_i);
CREATE INDEX daily_rainfall_2019_valid_idx on
  daily_rainfall_2019(valid);
  