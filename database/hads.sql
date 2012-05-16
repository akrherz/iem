--- $ createdb coop
--- $ psql -f /usr/pgsql-9.0/share/contrib/postgis-1.5/postgis.sql coop
--- $ psql -f /usr/pgsql-9.0/share/contrib/postgis-1.5/spatial_ref_sys.sql coop

---
--- Quasi synced from mesosite database
---
CREATE TABLE stations(
	id varchar(20),
	synop int,
	name varchar(64),
	state char(2),
	country char(2),
	elevation real,
	network varchar(20),
	online boolean,
	params varchar(300),
	county varchar(50),
	plot_name varchar(64),
	climate_site varchar(6),
	remote_id int,
	wfo char(3),
	archive_begin timestamp with time zone,
	archive_end timestamp with time zone,
	tzname varchar(32),
	modified timestamp with time zone,
	iemid int PRIMARY KEY
	);
SELECT AddGeometryColumn('stations', 'geom', 4326, 'POINT', 2);
GRANT SELECT on stations to nobody,apache;

CREATE TABLE raw2010(
	station varchar(8),
	valid timestamp with time zone,
	key varchar(8),
	value real
);

CREATE TABLE raw2010_12() inherits (raw2010);

CREATE TABLE unknown(
	nwsli varchar(8),
	product varchar(64),
	network varchar(24)
);
