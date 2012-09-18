---
--- Racoon Work Tasks
---
CREATE TABLE racoon_jobs(
  jobid varchar(32) default md5(random()::text),
  wfo varchar(3),
  sts timestamp with time zone,
  ets timestamp with time zone,
  radar varchar(3),
  processed boolean default false,
  nexrad_product char(3)
);
GRANT all on racoon_jobs to apache,nobody;

---
--- Oauth tokens
---
CREATE TABLE oauth_tokens(
  username text,
  token text,
  secret text
);

---
--- IEM Apps Database!
---
CREATE TABLE iemapps(
  appid serial unique,
  name varchar(256) unique not null,
  description text,
  url varchar(256) not null
);
GRANT ALL on iemapps to nobody,apache;

CREATE TABLE iemapps_tags(
	appid int references iemapps(appid),
	tag varchar(24) not null
);
CREATE UNIQUE INDEX iemapps_tags_idx on iemapps_tags(appid,tag);
GRANT ALL on iemapps_tags to nobody,apache;

---
--- El Nino
---
CREATE TABLE elnino(
  monthdate date,
  anom_34 real
);
GRANT SELECT on elnino to nobody,apache;

---
--- webcam logs
---
CREATE TABLE camera_log(
	cam varchar(11),
	valid timestamp with time zone,
	drct smallint);
CREATE INDEX camera_log_idx on camera_log(valid);
GRANT SELECT on camera_log to apache,nobody;

---
--- webcam currents
---
CREATE TABLE camera_current(
	cam varchar(11),
	valid timestamp with time zone,
	drct smallint);
GRANT SELECT on camera_current to apache,nobody;

---
--- Webcam scheduling
---
CREATE TABLE webcam_scheduler(
	cid varchar(10),
	begints timestamp with time zone,
	endts timestamp with time zone,
	is_daily boolean,
	filename varchar,
	movie_seconds smallint);
alter table webcam_scheduler SET with oids;	
CREATE UNIQUE index webcam_scheduler_filename_idx on
	webcam_scheduler(filename);
GRANT ALL on webcam_scheduler to nobody,apache;

---
--- Store IEM settings
---
CREATE TABLE properties(
  propname varchar,
  propvalue varchar
);
GRANT ALL on properties to apache,nobody;
CREATE UNIQUE index properties_idx on properties(propname, propvalue);

---
--- Webcam configurations
---
CREATE TABLE webcams(
	id varchar(11),
	ip inet,
	name varchar,
	pan0 smallint,
	online boolean,
	port int,
	network varchar(10),
	iservice varchar,
	iserviceurl varchar,
	sts timestamp with time zone,
	ets timestamp with time zone,
	county varchar,
	hosted varchar,
	hostedurl varchar,
	sponsor varchar,
	sponsorurl varchar,
	removed boolean,
	state varchar(2),
	moviebase varchar);
SELECT AddGeometryColumn('webcams', 'geom', 4326, 'POINT', 2);
GRANT select on webcams to apache,nobody;

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
	archive_begin date,
	archive_end timestamp with time zone,
	modified timestamp with time zone,
	tzname varchar(32),
	iemid SERIAL
);
CREATE UNIQUE index stations_idx on stations(id, network);
SELECT AddGeometryColumn('stations', 'geom', 4326, 'POINT', 2);
GRANT SELECT on stations to apache,nobody;
grant all on stations_iemid_seq to nobody,apache;

CREATE OR REPLACE FUNCTION update_modified_column()
	RETURNS TRIGGER AS $$
	BEGIN
	   NEW.modified = now(); 
	   RETURN NEW;
	END;
	$$ language 'plpgsql';
	
CREATE TRIGGER update_stations_modtime BEFORE UPDATE
        ON stations FOR EACH ROW EXECUTE PROCEDURE 
        update_modified_column();

---
create table iemmaps(
  id SERIAL,
  title varchar(256),
  entered timestamp with time zone DEFAULT now(),
  description text,
  keywords varchar(256),
  views int,
  ref varchar(32),
  category varchar(24)
);
GRANT all on iemmaps to apache,nobody;
GRANT all on iemmaps_id_seq to apache,nobody;

CREATE table feature(
  valid timestamp with time zone DEFAULT now(),
  title varchar(256),
  story text,
  caption varchar(256),
  good smallint,
  bad smallint,
  voting boolean,
  tags varchar(1024),
  fbid bigint);
CREATE unique index feature_title_check_idx on feature(title);
CREATE index feature_valid_idx on feature(valid);
GRANT all on feature to nobody,apache;
