CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (4, now());

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
);
GRANT SELECT on monthly_rainfall to nobody,apache;

CREATE TABLE monthly_rainfall_1997() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_1997 to nobody,apache;
ALTER TABLE monthly_rainfall_1997 add constraint __monthly_rainfall_1997__constraint
  CHECK(valid >= '1997-01-01'::date and valid < '1998-01-01'::date);
    

CREATE TABLE monthly_rainfall_1998() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_1998 to nobody,apache;
ALTER TABLE monthly_rainfall_1998 add constraint __monthly_rainfall_1998__constraint
  CHECK(valid >= '1998-01-01'::date and valid < '1999-01-01'::date);
    

CREATE TABLE monthly_rainfall_1999() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_1999 to nobody,apache;
ALTER TABLE monthly_rainfall_1999 add constraint __monthly_rainfall_1999__constraint
  CHECK(valid >= '1999-01-01'::date and valid < '2000-01-01'::date);
    

CREATE TABLE monthly_rainfall_2000() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2000 to nobody,apache;
ALTER TABLE monthly_rainfall_2000 add constraint __monthly_rainfall_2000__constraint
  CHECK(valid >= '2000-01-01'::date and valid < '2001-01-01'::date);
    

CREATE TABLE monthly_rainfall_2001() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2001 to nobody,apache;
ALTER TABLE monthly_rainfall_2001 add constraint __monthly_rainfall_2001__constraint
  CHECK(valid >= '2001-01-01'::date and valid < '2002-01-01'::date);
    

CREATE TABLE monthly_rainfall_2002() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2002 to nobody,apache;
ALTER TABLE monthly_rainfall_2002 add constraint __monthly_rainfall_2002__constraint
  CHECK(valid >= '2002-01-01'::date and valid < '2003-01-01'::date);
    

CREATE TABLE monthly_rainfall_2003() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2003 to nobody,apache;
ALTER TABLE monthly_rainfall_2003 add constraint __monthly_rainfall_2003__constraint
  CHECK(valid >= '2003-01-01'::date and valid < '2004-01-01'::date);
    

CREATE TABLE monthly_rainfall_2004() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2004 to nobody,apache;
ALTER TABLE monthly_rainfall_2004 add constraint __monthly_rainfall_2004__constraint
  CHECK(valid >= '2004-01-01'::date and valid < '2005-01-01'::date);
    

CREATE TABLE monthly_rainfall_2005() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2005 to nobody,apache;
ALTER TABLE monthly_rainfall_2005 add constraint __monthly_rainfall_2005__constraint
  CHECK(valid >= '2005-01-01'::date and valid < '2006-01-01'::date);
    

CREATE TABLE monthly_rainfall_2006() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2006 to nobody,apache;
ALTER TABLE monthly_rainfall_2006 add constraint __monthly_rainfall_2006__constraint
  CHECK(valid >= '2006-01-01'::date and valid < '2007-01-01'::date);
    

CREATE TABLE monthly_rainfall_2007() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2007 to nobody,apache;
ALTER TABLE monthly_rainfall_2007 add constraint __monthly_rainfall_2007__constraint
  CHECK(valid >= '2007-01-01'::date and valid < '2008-01-01'::date);
    

CREATE TABLE monthly_rainfall_2008() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2008 to nobody,apache;
ALTER TABLE monthly_rainfall_2008 add constraint __monthly_rainfall_2008__constraint
  CHECK(valid >= '2008-01-01'::date and valid < '2009-01-01'::date);
    

CREATE TABLE monthly_rainfall_2009() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2009 to nobody,apache;
ALTER TABLE monthly_rainfall_2009 add constraint __monthly_rainfall_2009__constraint
  CHECK(valid >= '2009-01-01'::date and valid < '2010-01-01'::date);
    

CREATE TABLE monthly_rainfall_2010() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2010 to nobody,apache;
ALTER TABLE monthly_rainfall_2010 add constraint __monthly_rainfall_2010__constraint
  CHECK(valid >= '2010-01-01'::date and valid < '2011-01-01'::date);
    

CREATE TABLE monthly_rainfall_2011() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2011 to nobody,apache;
ALTER TABLE monthly_rainfall_2011 add constraint __monthly_rainfall_2011__constraint
  CHECK(valid >= '2011-01-01'::date and valid < '2012-01-01'::date);
    

CREATE TABLE monthly_rainfall_2012() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2012 to nobody,apache;
ALTER TABLE monthly_rainfall_2012 add constraint __monthly_rainfall_2012__constraint
  CHECK(valid >= '2012-01-01'::date and valid < '2013-01-01'::date);
    

CREATE TABLE monthly_rainfall_2013() inherits (monthly_rainfall);
GRANT SELECT on monthly_rainfall_2013 to nobody,apache;
ALTER TABLE monthly_rainfall_2013 add constraint __monthly_rainfall_2013__constraint
  CHECK(valid >= '2013-01-01'::date and valid < '2014-01-01'::date);


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


CREATE TABLE daily_rainfall_1997() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_1997 to nobody,apache;
ALTER TABLE daily_rainfall_1997 add constraint __daily_rainfall_1997__constraint
  CHECK(valid >= '1997-01-01'::date and valid < '1998-01-01'::date);
CREATE INDEX daily_rainfall_1997_hrap_i_idx on
  daily_rainfall_1997(hrap_i);
CREATE INDEX daily_rainfall_1997_valid_idx on
  daily_rainfall_1997(valid);
    

CREATE TABLE daily_rainfall_1998() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_1998 to nobody,apache;
ALTER TABLE daily_rainfall_1998 add constraint __daily_rainfall_1998__constraint
  CHECK(valid >= '1998-01-01'::date and valid < '1999-01-01'::date);
CREATE INDEX daily_rainfall_1998_hrap_i_idx on
  daily_rainfall_1998(hrap_i);
CREATE INDEX daily_rainfall_1998_valid_idx on
  daily_rainfall_1998(valid);
    

CREATE TABLE daily_rainfall_1999() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_1999 to nobody,apache;
ALTER TABLE daily_rainfall_1999 add constraint __daily_rainfall_1999__constraint
  CHECK(valid >= '1999-01-01'::date and valid < '2000-01-01'::date);
CREATE INDEX daily_rainfall_1999_hrap_i_idx on
  daily_rainfall_1999(hrap_i);
CREATE INDEX daily_rainfall_1999_valid_idx on
  daily_rainfall_1999(valid);
    

CREATE TABLE daily_rainfall_2000() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2000 to nobody,apache;
ALTER TABLE daily_rainfall_2000 add constraint __daily_rainfall_2000__constraint
  CHECK(valid >= '2000-01-01'::date and valid < '2001-01-01'::date);
CREATE INDEX daily_rainfall_2000_hrap_i_idx on
  daily_rainfall_2000(hrap_i);
CREATE INDEX daily_rainfall_2000_valid_idx on
  daily_rainfall_2000(valid);
    

CREATE TABLE daily_rainfall_2001() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2001 to nobody,apache;
ALTER TABLE daily_rainfall_2001 add constraint __daily_rainfall_2001__constraint
  CHECK(valid >= '2001-01-01'::date and valid < '2002-01-01'::date);
CREATE INDEX daily_rainfall_2001_hrap_i_idx on
  daily_rainfall_2001(hrap_i);
CREATE INDEX daily_rainfall_2001_valid_idx on
  daily_rainfall_2001(valid);
    

CREATE TABLE daily_rainfall_2002() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2002 to nobody,apache;
ALTER TABLE daily_rainfall_2002 add constraint __daily_rainfall_2002__constraint
  CHECK(valid >= '2002-01-01'::date and valid < '2003-01-01'::date);
CREATE INDEX daily_rainfall_2002_hrap_i_idx on
  daily_rainfall_2002(hrap_i);
CREATE INDEX daily_rainfall_2002_valid_idx on
  daily_rainfall_2002(valid);
    

CREATE TABLE daily_rainfall_2003() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2003 to nobody,apache;
ALTER TABLE daily_rainfall_2003 add constraint __daily_rainfall_2003__constraint
  CHECK(valid >= '2003-01-01'::date and valid < '2004-01-01'::date);
CREATE INDEX daily_rainfall_2003_hrap_i_idx on
  daily_rainfall_2003(hrap_i);
CREATE INDEX daily_rainfall_2003_valid_idx on
  daily_rainfall_2003(valid);
    

CREATE TABLE daily_rainfall_2004() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2004 to nobody,apache;
ALTER TABLE daily_rainfall_2004 add constraint __daily_rainfall_2004__constraint
  CHECK(valid >= '2004-01-01'::date and valid < '2005-01-01'::date);
CREATE INDEX daily_rainfall_2004_hrap_i_idx on
  daily_rainfall_2004(hrap_i);
CREATE INDEX daily_rainfall_2004_valid_idx on
  daily_rainfall_2004(valid);
    

CREATE TABLE daily_rainfall_2005() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2005 to nobody,apache;
ALTER TABLE daily_rainfall_2005 add constraint __daily_rainfall_2005__constraint
  CHECK(valid >= '2005-01-01'::date and valid < '2006-01-01'::date);
CREATE INDEX daily_rainfall_2005_hrap_i_idx on
  daily_rainfall_2005(hrap_i);
CREATE INDEX daily_rainfall_2005_valid_idx on
  daily_rainfall_2005(valid);
    

CREATE TABLE daily_rainfall_2006() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2006 to nobody,apache;
ALTER TABLE daily_rainfall_2006 add constraint __daily_rainfall_2006__constraint
  CHECK(valid >= '2006-01-01'::date and valid < '2007-01-01'::date);
CREATE INDEX daily_rainfall_2006_hrap_i_idx on
  daily_rainfall_2006(hrap_i);
CREATE INDEX daily_rainfall_2006_valid_idx on
  daily_rainfall_2006(valid);
    

CREATE TABLE daily_rainfall_2007() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2007 to nobody,apache;
ALTER TABLE daily_rainfall_2007 add constraint __daily_rainfall_2007__constraint
  CHECK(valid >= '2007-01-01'::date and valid < '2008-01-01'::date);
CREATE INDEX daily_rainfall_2007_hrap_i_idx on
  daily_rainfall_2007(hrap_i);
CREATE INDEX daily_rainfall_2007_valid_idx on
  daily_rainfall_2007(valid);
    

CREATE TABLE daily_rainfall_2008() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2008 to nobody,apache;
ALTER TABLE daily_rainfall_2008 add constraint __daily_rainfall_2008__constraint
  CHECK(valid >= '2008-01-01'::date and valid < '2009-01-01'::date);
CREATE INDEX daily_rainfall_2008_hrap_i_idx on
  daily_rainfall_2008(hrap_i);
CREATE INDEX daily_rainfall_2008_valid_idx on
  daily_rainfall_2008(valid);
    

CREATE TABLE daily_rainfall_2009() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2009 to nobody,apache;
ALTER TABLE daily_rainfall_2009 add constraint __daily_rainfall_2009__constraint
  CHECK(valid >= '2009-01-01'::date and valid < '2010-01-01'::date);
CREATE INDEX daily_rainfall_2009_hrap_i_idx on
  daily_rainfall_2009(hrap_i);
CREATE INDEX daily_rainfall_2009_valid_idx on
  daily_rainfall_2009(valid);
    

CREATE TABLE daily_rainfall_2010() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2010 to nobody,apache;
ALTER TABLE daily_rainfall_2010 add constraint __daily_rainfall_2010__constraint
  CHECK(valid >= '2010-01-01'::date and valid < '2011-01-01'::date);
CREATE INDEX daily_rainfall_2010_hrap_i_idx on
  daily_rainfall_2010(hrap_i);
CREATE INDEX daily_rainfall_2010_valid_idx on
  daily_rainfall_2010(valid);
    

CREATE TABLE daily_rainfall_2011() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2011 to nobody,apache;
ALTER TABLE daily_rainfall_2011 add constraint __daily_rainfall_2011__constraint
  CHECK(valid >= '2011-01-01'::date and valid < '2012-01-01'::date);
CREATE INDEX daily_rainfall_2011_hrap_i_idx on
  daily_rainfall_2011(hrap_i);
CREATE INDEX daily_rainfall_2011_valid_idx on
  daily_rainfall_2011(valid);
    

CREATE TABLE daily_rainfall_2012() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2012 to nobody,apache;
ALTER TABLE daily_rainfall_2012 add constraint __daily_rainfall_2012__constraint
  CHECK(valid >= '2012-01-01'::date and valid < '2013-01-01'::date);
CREATE INDEX daily_rainfall_2012_hrap_i_idx on
  daily_rainfall_2012(hrap_i);
CREATE INDEX daily_rainfall_2012_valid_idx on
  daily_rainfall_2012(valid);
    

CREATE TABLE daily_rainfall_2013() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2013 to nobody,apache;
ALTER TABLE daily_rainfall_2013 add constraint __daily_rainfall_2013__constraint
  CHECK(valid >= '2013-01-01'::date and valid < '2014-01-01'::date);
CREATE INDEX daily_rainfall_2013_hrap_i_idx on
  daily_rainfall_2013(hrap_i);
CREATE INDEX daily_rainfall_2013_valid_idx on
  daily_rainfall_2013(valid);

CREATE TABLE daily_rainfall_2014() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2014 to nobody,apache;
ALTER TABLE daily_rainfall_2014 add constraint __daily_rainfall_2014__constraint
  CHECK(valid >= '2014-01-01'::date and valid < '2015-01-01'::date);
CREATE INDEX daily_rainfall_2014_hrap_i_idx on
  daily_rainfall_2014(hrap_i);
CREATE INDEX daily_rainfall_2014_valid_idx on
  daily_rainfall_2014(valid);
  
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
  
CREATE TABLE daily_rainfall_2018() inherits (daily_rainfall);
GRANT SELECT on daily_rainfall_2018 to nobody,apache;
ALTER TABLE daily_rainfall_2018 add constraint __daily_rainfall_2018__constraint
  CHECK(valid >= '2018-01-01'::date and valid < '2019-01-01'::date);
CREATE INDEX daily_rainfall_2018_hrap_i_idx on
  daily_rainfall_2018(hrap_i);
CREATE INDEX daily_rainfall_2018_valid_idx on
  daily_rainfall_2018(valid);

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
  