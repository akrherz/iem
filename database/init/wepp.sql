CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (5, now());

--- Tables loaded by shp2pgsql
---   + counties
---   + hrap_polygons
---   + hrap_utm
---   + iacounties
---   + iatwp

CREATE TABLE waterbalance(
 run_id bigint,
 valid date,
 vsm real,
 s10cm real,
 s20cm real,
 et real);
 CREATE TABLE waterbalance_by_twp(
  valid date,
  model_twp varchar(10),
  vsm real,
  vsm_stddev real,
  vsm_range real,
  s10cm real,
  s20cm real,
  et real);

CREATE TABLE soils(
 soil_id int,
 name varchar(100),
 texture varchar(25),
 layers int,
 albedo real,
 sat real,
 interrill real,
 rill real,
 shear real,
 conduct real,
 kfact real,
 kffact real,
 tfact real);
CREATE UNIQUE index soils_idx on soils(soil_id);

CREATE TABLE nri(
 id bigint,
 model_twp varchar,
 psu_id int,
 sample int,
 county_id int,
 town_id int,
 range_id int,
 len real,
 steep real,
 soil_id int,
 man_id int,
 ucfact real,
 upfact real,
 soil_depth int,
 slope real);
CREATE UNIQUE INDEX nri_id_idx on nri(id);
CREATE INDEX nri_man_id on nri(man_id);
CREATE INDEX nri_model_twp_idx on nri(model_twp);
GRANT SELECT on nri to apache,nobody;

CREATE TABLE layers(
 soil_id int,
 depth real,
 sand real,
 clay real,
 om real,
 cec real,
 rock real
);

CREATE TABLE managements(
  man_id int UNIQUE,
  name varchar(100)
);

CREATE TABLE mandetails(
 man_id int,
 seq int,
 mon int,
 day int,
 year int,
 op varchar(32),
 type varchar(100),
 comm varchar(64)
);

CREATE TABLE job_queue(
  id SERIAL UNIQUE,
  combo_id int,
  queued timestamptz,
  answered boolean,
  request_id int
);
CREATE INDEX job_combo_queue_id_key on job_queue(combo_id);

CREATE TABLE erosion_log(
 valid date UNIQUE);

---
--- Climate Sector wx data
CREATE TABLE climate_sectors(
  sector smallint,
  day date,
  high real default 0,
  low real default 0,
  rad real default 0,
  wvl real default 0,
  drct smallint default 0,
  dewp real default 0);
CREATE INDEX climate_sectors_idx on climate_sectors(sector,day);

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
) PARTITION by range(valid);
ALTER TABLE monthly_rainfall OWNER to mesonet;
GRANT SELECT on monthly_rainfall to nobody,apache;


 do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1997..2030
    loop
        mytable := format($f$monthly_rainfall_%s$f$,
            year);
        execute format($f$
            create table %s partition of monthly_rainfall
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            $f$, mytable,
            year, year +1);
        execute format($f$
            ALTER TABLE %s OWNER to mesonet
        $f$, mytable);
        execute format($f$
            GRANT ALL on %s to ldm
        $f$, mytable);
        execute format($f$
            GRANT SELECT on %s to nobody,apache
        $f$, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

---
--- Daily Rainfall
---
CREATE TABLE daily_rainfall(
  hrap_i smallint,
  valid date,
  rainfall real,
  peak_15min real,
  hr_cnt smallint
) PARTITION by range(valid);
ALTER TABLE daily_rainfall OWNER to mesonet;
GRANT SELECT on daily_rainfall to nobody,apache;

 do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1997..2030
    loop
        mytable := format($f$daily_rainfall_%s$f$,
            year);
        execute format($f$
            create table %s partition of daily_rainfall
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            $f$, mytable,
            year, year +1);
        execute format($f$
            ALTER TABLE %s OWNER to mesonet
        $f$, mytable);
        execute format($f$
            GRANT ALL on %s to ldm
        $f$, mytable);
        execute format($f$
            GRANT SELECT on %s to nobody,apache
        $f$, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_hrap_i_idx on %s(hrap_i)
        $f$, mytable, mytable);
    end loop;
end;
$do$;
