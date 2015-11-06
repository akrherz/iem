-- Remove old table 
DROP TABLE IF EXISTS quickstats;

-- Storage of NASS Quickstats
-- The following columns are not saved...
-- short_desc
-- domain_desc
-- domaincat_desc
-- state_ansi
-- state_fips_code
-- state_name
-- asd_desc
-- county_name
-- region_desc
-- watershed_desc
-- congr_district_code
-- country_name
-- location_desc
-- reference_period_desc


CREATE TABLE IF NOT EXISTS nass_quickstats(
	source_desc varchar(60),
	sector_desc varchar(60),
	group_desc varchar(80),
	commodity_desc varchar(80),
	class_desc varchar(180),
	prodn_practice_desc varchar(180),
	util_practice_desc varchar(180),
	statisticcat_desc varchar(80),
	unit_desc varchar(60),
	agg_level_desc varchar(40),
	state_alpha varchar(2),
	asd_code smallint,
	county_ansi smallint,
	zip_5 int,
	watershed_code int,
	country_code smallint,
	year int,
	freq_desc varchar(30),
	begin_code int,
	end_code int,
	week_ending date,
	load_time timestamptz,
	value varchar(24),
	cv varchar(7),
	num_value real
);
GRANT SELECT on nass_quickstats to nobody,apache;

