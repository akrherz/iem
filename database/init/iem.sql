CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (20, now());

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

---
--- Events table
---
CREATE TABLE events(
  station varchar(10),
  network varchar(10),
  valid timestamptz,
  event varchar(10),
  magnitude real,
  iemid int REFERENCES stations(iemid)
);
GRANT SELECT on events to nobody,apache;

---
--- Current QC data
---
CREATE TABLE current_qc(
  station varchar(10),
  valid timestamp without time zone,
  network varchar(10),
  tmpf real,
  tmpf_qc_av real,
  tmpf_qc_sc real,
  dwpf real,
  dwpf_qc_av real,
  dwpf_qc_sc real,  
  alti real,
  alti_qc_av real,
  alti_qc_sc real,
  iemid int REFERENCES stations(iemid)
 );
CREATE UNIQUE INDEX current_qc_idx on current_qc(station, network);
GRANT SELECT on current_qc to nobody,apache;

---
--- Copy of the climate51 table that is in the coop database
---
CREATE TABLE climate51(
  station varchar(6),
  valid date,
  high real,
  low real,
  precip real,
  snow real,
  max_high real,
  max_low real,
  min_high real,
  min_low real,
  max_precip real,
  years int,
  gdd50 real,
  sdd86 real,
  max_high_yr   int,
  max_low_yr    int,
  min_high_yr   int,
  min_low_yr    int,
  max_precip_yr int,
  max_range     smallint,
  min_range smallint,
  hdd65 real 
);
CREATE UNIQUE INDEX climate51_idx on climate51(station,valid);
CREATE INDEX climate51_station_idx on climate51(station);
CREATE INDEX climate51_valid_idx on climate51(valid);
GRANT SELECT on climate51 to nobody,apache;

---
--- Storage of information we parse from CLI products
---
CREATE TABLE cli_data(
  station char(4),
  product varchar(64),
  valid date,
  high int,
  high_normal int,
  high_record int,
  high_record_years int[],
  high_time varchar(7),
  low int,
  low_normal int,
  low_record int,
  low_record_years int[],
  low_time varchar(7),
  precip float,
  precip_month float,
  precip_jan1 float,
  precip_jan1_normal float,
  precip_jul1 float,
  precip_dec1 float,
  precip_dec1_normal float,
  precip_normal float,
  precip_record float,
  precip_record_years int[],
  precip_month_normal real,
  snow float,
  snow_month float,
  snow_jun1 float,
  snow_jul1 float,
  snow_dec1 float,
  snow_record_years int[],
  snow_record float,
  snow_jun1_normal float,
  snow_jul1_normal float,
  snow_dec1_normal float,
  snow_month_normal float,
  precip_jun1 real,
  precip_jun1_normal real,
  average_sky_cover real
);
CREATE UNIQUE index cli_data_idx on cli_data(station,valid);
GRANT SELECT on cli_data to nobody,apache;

---
--- Offline metadata
---
CREATE TABLE offline(
	station varchar(20),
	network varchar(10),
	trackerid int,
	valid timestamptz);
GRANT SELECT on offline to nobody,apache;


 create table current_shef(
   station varchar(10),
   valid timestamp with time zone,
   physical_code char(2),
   duration char(1),
   source char(2),
   extremum char(1),
   probability char(1),
   value real,
   depth smallint
   );
 create index current_shef_station_idx on current_shef(station);
 GRANT SELECT on current_shef to nobody;
 GRANT SELECT on current_shef to apache;
 
CREATE OR REPLACE RULE replace_current_shef AS ON 
    INSERT TO current_shef WHERE (EXISTS 
        (SELECT 1 FROM current_shef WHERE
        station = new.station and physical_code = new.physical_code and
        duration = new.duration and source = new.source and 
        extremum = new.extremum and ((new.depth is null and depth is null) or 
        depth = new.depth))) DO INSTEAD 
        UPDATE current_shef SET value = new.value, valid = new.valid 
        WHERE station = new.station and physical_code = new.physical_code and
        duration = new.duration and source = new.source and 
        extremum = new.extremum and valid < new.valid and 
        ((new.depth is null and depth is null) or depth = new.depth);


CREATE TABLE current_tmp(
    iemid int REFERENCES stations(iemid),
    tmpf real,
    dwpf real,
    drct real,
    sknt real,
    indoor_tmpf real,
    tsf0 real,
    tsf1 real,
    tsf2 real,
    tsf3 real,
    rwis_subf real,
    scond0 character varying,
    scond1 character varying,
    scond2 character varying,
    scond3 character varying,
    valid timestamp with time zone DEFAULT '1980-01-01 00:00:00-06'::timestamp with time zone,
    pday real,
    c1smv real,
    c2smv real,
    c3smv real,
    c4smv real,
    c5smv real,
    c1tmpf real,
    c2tmpf real,
    c3tmpf real,
    c4tmpf real,
    c5tmpf real,
    pres real,
    relh real,
    srad real,
    vsby real,
    phour real DEFAULT (-99),
    gust real,
    raw character varying(256),
    alti real,
    mslp real,
    qc_tmpf character(1),
    qc_dwpf character(1),
    rstage real,
    ozone real,
    co2 real,
    pmonth real,
    skyc1 character(3),
    skyc2 character(3),
    skyc3 character(3),
    skyl1 integer,
    skyl2 integer,
    skyl3 integer,
    skyc4 character(3),
    skyl4 integer,
    pcounter real,
    discharge real,
    p03i real,
    p06i real,
    p24i real,
    max_tmpf_6hr real,
    min_tmpf_6hr real,
    max_tmpf_24hr real,
    min_tmpf_24hr real,
    wxcodes varchar(12)[],
    battery real,
    water_tmpf real,
    feel real,
    ice_accretion_1hr real,
    ice_accretion_3hr real,
    ice_accretion_6hr real,
    peak_wind_gust real,
    peak_wind_drct real,
    peak_wind_time timestamptz
);

CREATE TABLE current (
    iemid int REFERENCES stations(iemid),
    tmpf real,
    dwpf real,
    drct real,
    sknt real,
    indoor_tmpf real,
    tsf0 real,
    tsf1 real,
    tsf2 real,
    tsf3 real,
    rwis_subf real,
    scond0 character varying,
    scond1 character varying,
    scond2 character varying,
    scond3 character varying,
    valid timestamp with time zone DEFAULT '1980-01-01 00:00:00-06'::timestamp with time zone,
    pday real,
    c1smv real,
    c2smv real,
    c3smv real,
    c4smv real,
    c5smv real,
    c1tmpf real,
    c2tmpf real,
    c3tmpf real,
    c4tmpf real,
    c5tmpf real,
    pres real,
    relh real,
    srad real,
    vsby real,
    phour real DEFAULT (-99),
    gust real,
    raw character varying(256),
    alti real,
    mslp real,
    qc_tmpf character(1),
    qc_dwpf character(1),
    rstage real,
    ozone real,
    co2 real,
    pmonth real,
    skyc1 character(3),
    skyc2 character(3),
    skyc3 character(3),
    skyl1 integer,
    skyl2 integer,
    skyl3 integer,
    skyc4 character(3),
    skyl4 integer,
    pcounter real,
    discharge real,
    p03i real,
    p06i real,
    p24i real,
    max_tmpf_6hr real,
    min_tmpf_6hr real,
    max_tmpf_24hr real,
    min_tmpf_24hr real,
    wxcodes varchar(12)[],
    battery real,
    water_tmpf real,
    feel real,
    ice_accretion_1hr real,
    ice_accretion_3hr real,
    ice_accretion_6hr real,
    peak_wind_gust real,
    peak_wind_drct real,
    peak_wind_time timestamptz
);
CREATE UNIQUE index current_iemid_idx on current(iemid);
GRANT SELECT on current to apache,nobody;

CREATE TABLE current_log (
    iemid int REFERENCES stations(iemid),
    tmpf real,
    dwpf real,
    drct real,
    sknt real,
    indoor_tmpf real,
    tsf0 real,
    tsf1 real,
    tsf2 real,
    tsf3 real,
    rwis_subf real,
    scond0 character varying,
    scond1 character varying,
    scond2 character varying,
    scond3 character varying,
    valid timestamp with time zone DEFAULT '1980-01-01 00:00:00-06'::timestamp with time zone,
    pday real,
    c1smv real,
    c2smv real,
    c3smv real,
    c4smv real,
    c5smv real,
    c1tmpf real,
    c2tmpf real,
    c3tmpf real,
    c4tmpf real,
    c5tmpf real,
    pres real,
    relh real,
    srad real,
    vsby real,
    phour real DEFAULT (-99),
    gust real,
    raw character varying(256),
    alti real,
    mslp real,
    qc_tmpf character(1),
    qc_dwpf character(1),
    rstage real,
    ozone real,
    co2 real,
    pmonth real,
    skyc1 character(3),
    skyc2 character(3),
    skyc3 character(3),
    skyl1 integer,
    skyl2 integer,
    skyl3 integer,
    skyc4 character(3),
    skyl4 integer,
    pcounter real,
    discharge real,
    p03i real,
    p06i real,
    p24i real,
    max_tmpf_6hr real,
    min_tmpf_6hr real,
    max_tmpf_24hr real,
    min_tmpf_24hr real,
    wxcodes varchar(12)[],
    battery real,
    water_tmpf real,
    feel real,
    ice_accretion_1hr real,
    ice_accretion_3hr real,
    ice_accretion_6hr real,
    peak_wind_gust real,
    peak_wind_drct real,
    peak_wind_time timestamptz
);
GRANT ALL on current_log to mesonet,ldm;
GRANT SELECT on current_log to apache,nobody;

CREATE OR REPLACE FUNCTION current_update_log() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  BEGIN
   IF (NEW.valid != OLD.valid) THEN
     INSERT into current_log SELECT * from current WHERE iemid = NEW.iemid;
   END IF;
   RETURN NEW;
  END
 $$;

CREATE TRIGGER current_update_tigger AFTER UPDATE ON current 
FOR EACH ROW EXECUTE PROCEDURE current_update_log();

-- main storage of summary data
CREATE TABLE summary (
	iemid int REFERENCES stations(iemid),
    max_tmpf real,
    min_tmpf real,
    day date,
    max_sknt real,
    max_gust real,
    max_sknt_ts timestamp with time zone,
    max_gust_ts timestamp with time zone,
    max_dwpf real,
    min_dwpf real,
    pday real,
    pmonth real,
    snow real,
    snowd real,
    max_tmpf_qc character(1),
    min_tmpf_qc character(1),
    pday_qc character(1),
    snow_qc character(1),
    snoww real,
    max_drct real,
    max_srad smallint,
    coop_tmpf real,
    coop_valid timestamp with time zone,
    et_inch real,
    srad_mj real,
    avg_sknt real,
    vector_avg_drct real,
    avg_rh real,
    min_rh real,
    max_rh real,
    max_water_tmpf real,
    min_water_tmpf real,
    max_feel real,
    avg_feel real,
    min_feel real
) PARTITION by range(day);
ALTER TABLE summary OWNER to mesonet;
GRANT ALL on summary to ldm;
GRANT SELECT on summary to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1928..2030
    loop
        mytable := format($f$summary_%s$f$, year);
        execute format($f$
            create table %s partition of summary
            for values from ('%s-01-01') to ('%s-01-01')
            $f$, mytable, year, year + 1);
        execute format($f$
            ALTER TABLE %s ADD foreign key(iemid)
            references stations(iemid) ON DELETE CASCADE;
        $f$, mytable);
        execute format($f$
            ALTER TABLE %s OWNER to mesonet
        $f$, mytable);
        execute format($f$
            GRANT ALL on %s to ldm
        $f$, mytable);
        execute format($f$
            GRANT SELECT on %s to nobody,apache
        $f$, mytable);
        -- Indices
        execute format($f$
            CREATE INDEX %s_idx on %s(iemid, day)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_day_idx on %s(day)
        $f$, mytable, mytable);
    end loop;
end;
$do$;


---
--- Hourly precip
---
CREATE TABLE hourly(
  station varchar(20),
  network varchar(10),
  valid timestamptz,
  phour real,
  iemid int references stations(iemid)
) PARTITION by range(valid);
ALTER TABLE hourly OWNER to mesonet;
GRANT ALL on hourly to ldm;
GRANT SELECT on hourly to apache,nobody;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1941..2030
    loop
        mytable := format($f$hourly_%s$f$, year);
        execute format($f$
            create table %s partition of hourly
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
            $f$, mytable, year, year + 1);
        execute format($f$
            ALTER TABLE %s ADD foreign key(iemid)
            references stations(iemid) ON DELETE CASCADE;
        $f$, mytable);
        execute format($f$
CREATE RULE replace_%s as
    ON INSERT TO %s
   WHERE (EXISTS ( SELECT 1
           FROM %s
          WHERE %s.station::text = new.station::text
          AND %s.network::text = new.network::text
          AND %s.valid = new.valid)) DO INSTEAD
         UPDATE %s SET phour = new.phour
  WHERE %s.station::text = new.station::text AND
  %s.network::text = new.network::text AND
  %s.valid = new.valid
        $f$, mytable, mytable, mytable, mytable, mytable,
        mytable, mytable, mytable, mytable, mytable);
        execute format($f$
            ALTER TABLE %s OWNER to mesonet
        $f$, mytable);
        execute format($f$
            GRANT ALL on %s to ldm
        $f$, mytable);
        execute format($f$
            GRANT SELECT on %s to nobody,apache
        $f$, mytable);
        -- Indices
        execute format($f$
            CREATE INDEX %s_idx on %s(station, network, valid)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_valid_idx on %s(valid)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

---

CREATE TABLE rwis_locations(
  id smallint UNIQUE,
  nwsli char(5)
);
grant select on rwis_locations to nobody,apache;

--
-- RWIS Deep Soil Probe Data
--
CREATE TABLE rwis_soil_data(
  location_id smallint references rwis_locations(id),
  sensor_id smallint,
  valid timestamp with time zone,
  temp real,
  moisture real
);
CREATE TABLE rwis_soil_data_log(
  location_id smallint references rwis_locations(id),
  sensor_id smallint,
  valid timestamp with time zone,
  temp real,
  moisture real
);

GRANT select on rwis_soil_data to apache,nobody;

CREATE FUNCTION rwis_soil_update_log() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  BEGIN
   IF (NEW.valid != OLD.valid) THEN
     INSERT into rwis_soil_data_log 
        SELECT * from rwis_soil_data WHERE sensor_id = NEW.sensor_id
        and location_id = NEW.location_id;
   END IF;
   RETURN NEW;
  END
 $$;

CREATE TRIGGER rwis_soil_update_tigger
    AFTER UPDATE ON rwis_soil_data
    FOR EACH ROW
    EXECUTE PROCEDURE rwis_soil_update_log();

--
-- RWIS Traffic Data Storage
-- 
CREATE TABLE rwis_traffic_sensors(
  id SERIAL UNIQUE,
  location_id smallint references rwis_locations(id),
  lane_id smallint,
  name varchar(64)
);

CREATE OR REPLACE view rwis_traffic_meta AS 
  SELECT l.id as location_id, l.nwsli as nwsli, s.id as sensor_id,
  s.lane_id as lane_id
  FROM rwis_locations l, rwis_traffic_sensors s WHERE
  l.id = s.location_id;


CREATE TABLE rwis_traffic_data(
  sensor_id int references rwis_traffic_sensors(id),
  valid timestamp with time zone,
  avg_speed real,
  avg_headway real,
  normal_vol real,
  long_vol real,
  occupancy real
);

CREATE TABLE rwis_traffic_data_log(
  sensor_id int references rwis_traffic_sensors(id),
  valid timestamp with time zone,
  avg_speed real,
  avg_headway real,
  normal_vol real,
  long_vol real,
  occupancy real
);

CREATE FUNCTION rwis_traffic_update_log() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  BEGIN
   IF (NEW.valid != OLD.valid) THEN
     INSERT into rwis_traffic_data_log 
        SELECT * from rwis_traffic_data WHERE sensor_id = NEW.sensor_id;
   END IF;
   RETURN NEW;
  END
 $$;

CREATE TRIGGER rwis_traffic_update_tigger
    AFTER UPDATE ON rwis_traffic_data
    FOR EACH ROW
    EXECUTE PROCEDURE rwis_traffic_update_log();


CREATE VIEW rwis_traffic AS 
  SELECT * from 
  rwis_traffic_sensors s, rwis_traffic_data d
  WHERE d.sensor_id = s.id;

GRANT SELECT on rwis_traffic_data to apache,nobody;
GRANT SELECT on rwis_traffic_data_log to apache,nobody;
GRANT SELECT on rwis_traffic_sensors to apache,nobody;
GRANT SELECT on rwis_traffic to apache,nobody;

INSERT into rwis_locations values (58, 'RPFI4');
INSERT into rwis_locations values (30, 'RMCI4');
INSERT into rwis_locations values (54, 'RSYI4');
INSERT into rwis_locations values (42, 'RSPI4');
INSERT into rwis_locations values (48, 'RWBI4');
INSERT into rwis_locations values (22, 'RGRI4');
INSERT into rwis_locations values (45, 'RURI4');
INSERT into rwis_locations values (43, 'RSLI4');
INSERT into rwis_locations values (60, 'RDNI4');
INSERT into rwis_locations values (61, 'RQCI4');
INSERT into rwis_locations values (57, 'RTMI4');
INSERT into rwis_locations values (49, 'RHAI4');
INSERT into rwis_locations values (52, 'RCRI4');
INSERT into rwis_locations values (53, 'RCFI4');
INSERT into rwis_locations values (02, 'RTNI4');
INSERT into rwis_locations values (03, 'RTOI4');
INSERT into rwis_locations values (00, 'RDAI4');
INSERT into rwis_locations values (01, 'RALI4');
INSERT into rwis_locations values (06, 'RAVI4');
INSERT into rwis_locations values (07, 'RBUI4');
INSERT into rwis_locations values (04, 'RAMI4');
INSERT into rwis_locations values (05, 'RAKI4');
INSERT into rwis_locations values (46, 'RWLI4');
INSERT into rwis_locations values (47, 'RWII4');
INSERT into rwis_locations values (08, 'RCAI4');
INSERT into rwis_locations values (09, 'RCDI4');
INSERT into rwis_locations values (28, 'RMQI4');
INSERT into rwis_locations values (29, 'RMTI4');
INSERT into rwis_locations values (40, 'RSGI4');
INSERT into rwis_locations values (41, 'RSCI4');
INSERT into rwis_locations values (59, 'RCTI4');
INSERT into rwis_locations values (51, 'RIGI4');
INSERT into rwis_locations values (24, 'RIOI4');
INSERT into rwis_locations values (56, 'RDYI4');
INSERT into rwis_locations values (25, 'RJFI4');
INSERT into rwis_locations values (39, 'RSDI4');
INSERT into rwis_locations values (26, 'RLEI4');
INSERT into rwis_locations values (27, 'RMNI4');
INSERT into rwis_locations values (20, 'RDBI4');
INSERT into rwis_locations values (38, 'RROI4');
INSERT into rwis_locations values (21, 'RFDI4');
INSERT into rwis_locations values (11, 'RCNI4');
INSERT into rwis_locations values (10, 'RCII4');
INSERT into rwis_locations values (13, 'RCEI4');
INSERT into rwis_locations values (12, 'RCBI4');
INSERT into rwis_locations values (15, 'RDCI4');
INSERT into rwis_locations values (14, 'RDVI4');
INSERT into rwis_locations values (17, 'RDMI4');
INSERT into rwis_locations values (16, 'RDSI4');
INSERT into rwis_locations values (19, 'RDWI4');
INSERT into rwis_locations values (18, 'RDEI4');
INSERT into rwis_locations values (31, 'RMVI4');
INSERT into rwis_locations values (23, 'RIAI4');
INSERT into rwis_locations values (37, 'RPLI4');
INSERT into rwis_locations values (36, 'ROTI4');
INSERT into rwis_locations values (35, 'ROSI4');
INSERT into rwis_locations values (34, 'RONI4');
INSERT into rwis_locations values (33, 'RNHI4');
INSERT into rwis_locations values (55, 'RBFI4');
INSERT into rwis_locations values (32, 'RMPI4');
INSERT into rwis_locations values (44, 'RTPI4');
INSERT into rwis_locations values (50, 'RSBI4');


CREATE FUNCTION dzvalid(timestamp with time zone) RETURNS date
    LANGUAGE sql IMMUTABLE
    AS $_$SET TIME ZONE 'GMT'; select date($1)$_$;

CREATE FUNCTION getskyc(character varying) RETURNS smallint
    LANGUAGE sql
    AS $_$select value from skycoverage where code = $1$_$;


CREATE FUNCTION local_date(timestamp with time zone) RETURNS date
    LANGUAGE sql IMMUTABLE
    AS $_$select date($1)$_$;

CREATE FUNCTION mdate(timestamp with time zone) RETURNS date
    LANGUAGE sql IMMUTABLE
    AS $_$select date($1)$_$;

CREATE FUNCTION zero_record(text) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
  BEGIN
    UPDATE current SET tmpf = NULL, dwpf = NULL, drct = NULL,
     sknt = NULL  WHERE station = $1;
    RETURN true;
  END;
$_$;



  --
-- Set cascading deletes when an entry is removed from the stations table
--
ALTER TABLE current
  DROP CONSTRAINT current_iemid_fkey,
  ADD CONSTRAINT current_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE current_log
  DROP CONSTRAINT current_log_iemid_fkey,
  ADD CONSTRAINT current_log_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE current_qc
  DROP CONSTRAINT current_qc_iemid_fkey,
  ADD CONSTRAINT current_qc_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE current_tmp
  DROP CONSTRAINT current_tmp_iemid_fkey,
  ADD CONSTRAINT current_tmp_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE events
  DROP CONSTRAINT events_iemid_fkey,
  ADD CONSTRAINT events_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE hourly
  DROP CONSTRAINT hourly_iemid_fkey,
  ADD CONSTRAINT hourly_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary_2014
  DROP CONSTRAINT summary_2014_iemid_fkey,
  ADD CONSTRAINT summary_2014_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary_2015
  DROP CONSTRAINT summary_2015_iemid_fkey,
  ADD CONSTRAINT summary_2015_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary
  DROP CONSTRAINT summary_iemid_fkey,
  ADD CONSTRAINT summary_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
