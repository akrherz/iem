-- Storage of Winter Road Conditions for 2015 - 2016
CREATE TABLE roads_2015_2016_log(
	segid int REFERENCES roads_base(segid),
	valid timestamptz,
	cond_code smallint REFERENCES roads_conditions(code),
	towing_prohibited boolean,
	limited_vis boolean,
	raw varchar);
GRANT SELECT on roads_2015_2016_log to nobody;

-- Remove unused(?) column
ALTER TABLE roads_base DROP tempval;

-- Rename old log tables to be more explicit!
ALTER TABLE roads_2015_log RENAME to roads_2014_2015_log;
ALTER TABLE roads_2014_log RENAME to roads_2013_2014_log;
ALTER TABLE roads_2013_log RENAME to roads_2012_2013_log;
ALTER TABLE roads_2012_log RENAME to roads_2011_2012_log;
ALTER TABLE roads_2011_log RENAME to roads_2010_2011_log;
ALTER TABLE roads_2010_log RENAME to roads_2009_2010_log;
ALTER TABLE roads_2009_log RENAME to roads_2008_2009_log;
ALTER TABLE roads_2008_log RENAME to roads_2007_2008_log;
ALTER TABLE roads_2007_log RENAME to roads_2006_2007_log;
ALTER TABLE roads_2006_log RENAME to roads_2005_2006_log;
ALTER TABLE roads_2005_log RENAME to roads_2004_2005_log;
ALTER TABLE roads_2004_log RENAME to roads_2003_2004_log;

-- drop legacy roads_base tables
DROP TABLE roads_base_2005;
DROP TABLE roads_base_2006;
DROP TABLE roads_base_2009;
DROP TABLE roads_base_2010;
DROP TABLE roads_base_2011;
DROP TABLE roads_base_2013;
