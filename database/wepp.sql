---
--- Rainfall log
---
CREATE TABLE rainfall_log(
  valid date,
  max_rainfall real
);
GRANT SELECT on rainfall_log to nobody,apache;

---
--- Yearly Rainfall
---
CREATE TABLE yearly_rainfall(
  hrap_i smallint,
  valid date,
  rainfall real,
  peak_15min real,
  hr_cnt smallint
);
GRANT SELECT on yearly_rainfall to nobody,apache;

---
--- Monthly Rainfall
---
CREATE TABLE monthly_rainfall(
  hrap_i smallint,
  valid date,
  rainfall real,
  peak_15min real,
  hr_cnt smallint
);
GRANT SELECT on monthly_rainfall to nobody,apache;

CREATE TABLE monthly_rainfall_2013() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2013 to nobody,apache;

ALTER TABLE monthly_rainfall_2013 add constraint __monthly_rainfall_2013__constraint
  CHECK(valid >= '2013-01-01'::date and valid < '2014-01-01'::date);

---
--- Daily Rainfall
---
CREATE TABLE daily_rainfall(
  hrap_i smallint,
  valid date,
  rainfall real,
  peak_15min real,
  hr_cnt real
);
GRANT SELECT on daily_rainfall to nobody,apache;

CREATE TABLE daily_rainfall_2013() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2013 to nobody,apache;

ALTER TABLE daily_rainfall_2013 add constraint __daily_rainfall_2013__constraint
  CHECK(valid >= '2013-01-01'::date and valid < '2014-01-01'::date);

CREATE INDEX daily_rainfall_2013_hrap_i_idx on
  daily_rainfall_2013(hrap_i);
CREATE INDEX daily_rainfall_2013_valid_idx on
  daily_rainfall_2013(valid);