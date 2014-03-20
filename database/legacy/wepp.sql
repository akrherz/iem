---
--- Results by township by year
---
CREATE TABLE results_twp_year(
	model_twp varchar(9),
	valid date,
	avg_loss real,
	avg_runoff real,
	min_loss real,
	max_loss real,
	min_runoff real,
	max_runoff real,
	ve_runoff real,
	ve_loss real
);
GRANT SELECT on results_twp_year to nobody,apache;

---
--- Results by township by month
---
CREATE TABLE results_twp_month(
	model_twp varchar(9),
	valid date,
	avg_loss real,
	avg_runoff real,
	min_loss real,
	max_loss real,
	min_runoff real,
	max_runoff real,
	ve_runoff real,
	ve_loss real
);
GRANT SELECT on results_twp_month to nobody,apache;

---
--- Combinations
---
CREATE TABLE combos(
	id SERIAL UNIQUE,
	nri_id bigint,
	model_twp varchar(9),
	hrap_i int,
	mkrun boolean,
	erosivity_idx real
);
CREATE UNIQUE INDEX combos_idx on combos(nri_id, model_twp, hrap_i);
CREATE INDEX combos_hrap_i_idx on combos(hrap_i);
CREATE INDEX combos_model_twp_idx on combos(model_twp);
CREATE INDEX combos_nri_id_idx on combos(nri_id);
GRANT SELECT on combos to nobody,apache;

---
--- Store run results
---
CREATE TABLE results(
	run_id bigint,
	valid date,
	runoff real,
	loss real,
	precip real
);
CREATE INDEX results_run_id_idx on results(run_id);
CREATE INDEX results_valid_idx on results(valid);
GRANT SELECT on results to nobody,apache;

---
--- Store Results by Township
---
CREATE TABLE results_by_twp(
  model_twp varchar(9),
  valid date,
  avg_precip real,
  max_precip real,
  min_loss real,
  avg_loss real,
  max_loss real,
  min_runoff real,
  max_runoff real,
  avg_runoff real,
  bogus real,
  run_points int,
  min_precip real,
  ve_runoff real,
  ve_loss real
);
CREATE INDEX results_by_twp_model_twp_idx on results_by_twp(model_twp);
CREATE INDEX results_by_twp_valid_idx on results_by_twp(valid);
GRANT SELECT on results_by_twp to nobody,apache;

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

CREATE TABLE monthly_rainfall_2014() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2014 to nobody,apache;

ALTER TABLE monthly_rainfall_2014 add constraint __monthly_rainfall_2014__constraint
  CHECK(valid >= '2014-01-01'::date and valid < '2015-01-01'::date);

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

CREATE TABLE daily_rainfall_2014() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2014 to nobody,apache;

ALTER TABLE daily_rainfall_2014 add constraint __daily_rainfall_2014__constraint
  CHECK(valid >= '2014-01-01'::date and valid < '2015-01-01'::date);

CREATE INDEX daily_rainfall_2014_hrap_i_idx on
  daily_rainfall_2014(hrap_i);
CREATE INDEX daily_rainfall_2014_valid_idx on
  daily_rainfall_2014(valid);