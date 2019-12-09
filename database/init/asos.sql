CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (11, now());

---
--- Store unknown stations
---
CREATE TABLE unknown(
  id varchar(5),
  valid timestamptz
);

---
--- Some skycoverage metadata
---
CREATE TABLE skycoverage(
  code char(3),
  value smallint);
GRANT SELECT on skycoverage to nobody,apache;
INSERT into skycoverage values('CLR', 0);
INSERT into skycoverage values('FEW', 25);
INSERT into skycoverage values('SCT', 50);
INSERT into skycoverage values('BKN', 75);
INSERT into skycoverage values('OVC', 100);


CREATE FUNCTION getskyc(character varying) RETURNS smallint
    LANGUAGE sql
    AS $_$select value from skycoverage where code = $1$_$;


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
	nwn_id int,
	spri smallint,
	wfo varchar(3),
	archive_begin timestamptz,
	archive_end timestamp with time zone,
	modified timestamp with time zone,
	tzname varchar(32),
	iemid SERIAL,
	metasite boolean,
	sigstage_low real,
	sigstage_action real,
	sigstage_bankfull real,
	sigstage_flood real,
	sigstage_moderate real,
	sigstage_major real,
	sigstage_record real,
	ugc_county char(6),
	ugc_zone char(6),
	ncdc81 varchar(11),
	temp24_hour smallint,
	precip24_hour smallint
);
CREATE UNIQUE index stations_idx on stations(id, network);
create UNIQUE index stations_iemid_idx on stations(iemid);
SELECT AddGeometryColumn('stations', 'geom', 4326, 'POINT', 2);
GRANT SELECT on stations to apache,nobody;
grant all on stations_iemid_seq to nobody,apache;
GRANT ALL on stations to mesonet,ldm;
GRANT ALL on stations_iemid_seq to mesonet,ldm;

-- Storage of Type of Observation this is
CREATE TABLE alldata_report_type(
  id smallint UNIQUE NOT NULL,
  label varchar);
GRANT SELECT on alldata_report_type to nobody,apache;

INSERT into alldata_report_type VALUES
        (0, 'Unknown'),
        (1, 'MADIS HFMETAR'),
        (2, 'Routine'),
        (3, 'Special');


CREATE TABLE alldata(
 station        character varying(4),    
 valid          timestamp with time zone,
 tmpf           real,          
 dwpf           real,          
 drct           real,        
 sknt           real,         
 alti           real,      
 gust           real,       
 vsby           real,      
 skyc1          character(3),     
 skyc2          character(3),    
 skyc3          character(3),   
 skyl1          integer,  
 skyl2          integer, 
 skyl3          integer,
 metar          character varying(256),
 skyc4          character(3),
 skyl4          integer,
 p03i           real,
 p06i           real,
 p24i           real,
 max_tmpf_6hr   real,
 min_tmpf_6hr   real,
 max_tmpf_24hr  real,
 min_tmpf_24hr  real,
 mslp           real,
 p01i           real,
 wxcodes        varchar(12)[],
  report_type smallint REFERENCES alldata_report_type(id),
  ice_accretion_1hr real,
  ice_accretion_3hr real,
  ice_accretion_6hr real,
  feel real,
  relh real,
  peak_wind_gust real,
  peak_wind_drct real,
  peak_wind_time timestamptz
) PARTITION by range(valid);
ALTER TABLE alldata OWNER to mesonet;
GRANT ALL on alldata to ldm;
GRANT SELECT on alldata to nobody,apache;

do
$do$
declare
     year int;
begin
    for year in 1928..2030
    loop
        execute format($f$
            create table t%s partition of alldata
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            $f$, year, year, year + 1);
        execute format($f$
            ALTER TABLE t%s OWNER to mesonet
        $f$, year);
        execute format($f$
            GRANT ALL on t%s to ldm
        $f$, year);
        execute format($f$
            GRANT SELECT on t%s to nobody,apache
        $f$, year);
        -- Indices
        execute format($f$
            CREATE INDEX t%s_valid_idx on t%s(valid)
        $f$, year, year);
        execute format($f$
            CREATE INDEX t%s_station_idx on t%s(station)
        $f$, year, year);
    end loop;
end;
$do$;

---
--- One Minute ASOS data
---
CREATE TABLE alldata_1minute(
  station char(3),
  valid timestamptz,
  vis1_coeff real,
  vis1_nd char(1),
  vis2_coeff real,
  vis2_nd char(1),
  drct smallint,
  sknt smallint,
  gust_drct smallint,
  gust_sknt smallint,
  ptype char(2),
  precip real,
  pres1 real,
  pres2 real,
  pres3 real,
  tmpf smallint,
  dwpf smallint
) PARTITION by range(valid);
ALTER TABLE alldata_1minute OWNER to mesonet;
GRANT ALL on alldata_1minute to ldm;
GRANT SELECT on alldata_1minute to nobody,apache;

do
$do$
declare
     year int;
begin
    for year in 2000..2030
    loop
        execute format($f$
            create table t%s_1minute partition of alldata_1minute
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            $f$, year, year, year + 1);
        execute format($f$
            ALTER TABLE t%s_1minute OWNER to mesonet
        $f$, year);
        execute format($f$
            GRANT ALL on t%s_1minute to ldm
        $f$, year);
        execute format($f$
            GRANT SELECT on t%s_1minute to nobody,apache
        $f$, year);
        -- Indices
        execute format($f$
            CREATE INDEX t%s_1minute_valid_idx on t%s(valid)
        $f$, year, year);
        execute format($f$
            CREATE INDEX t%s_1minute_station_idx on t%s(station)
        $f$, year, year);
    end loop;
end;
$do$;
