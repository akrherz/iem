CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (18, now());

--- ==== TABLES TO investigate deleting
--- counties
--- cwas
--- states
--- tz_world  (scripts/dbutil/set_timezone.py)


---
--- Store metadata used to drive the /timemachine/
---
CREATE TABLE archive_products(
	id SERIAL,
	name varchar,
	template varchar,
	sts timestamptz,
	interval int,
	groupname varchar,
	time_offset int,
	avail_lag int);
GRANT SELECT on archive_products to nobody,apache;

CREATE TABLE iembot_room_syndications (
	roomname character varying(64),    
	endpoint character varying(64),    
	convtype character(1));


CREATE TABLE iembot_fb_access_tokens (
    fbpid bigint,
    access_token text
);
CREATE TABLE iembot_fb_subscriptions (
    fbpid bigint,
    channel character varying
);

---
--- Table to track iembot's use of social media
---
CREATE TABLE iembot_social_log(
  valid timestamp with time zone default now(),
  medium varchar(24),
  source varchar(256),
  resource_uri varchar(256),
  message text,
  message_link varchar(256),
  response text,
  response_code int
);
CREATE index iembot_social_log_valid_idx on iembot_social_log(valid);

---
--- networks we process!
---
CREATE TABLE networks(
  id varchar(12) unique,
  name varchar,
  tzname varchar(32)
);
GRANT SELECT on networks to nobody,apache;
SELECT AddGeometryColumn('networks', 'extent', 4326, 'POLYGON', 2);

---
--- Missing table: news
---
CREATE TABLE news(
  id serial not null,
  entered timestamptz default now(),
  body text,
  author varchar(100),
  title varchar(100),
  url varchar,
  views smallint default 0,
  tags varchar(128)[]);
CREATE INDEX news_entered_idx on news(entered);
GRANT ALL on news to nobody,apache;
GRANT ALL on news_id_seq to nobody,apache;

---
--- IEMBOT Twitter Page subscriptions
---
CREATE TABLE iembot_twitter_oauth(
  user_id bigint NOT NULL UNIQUE,
  screen_name text,
  access_token text,
  access_token_secret text,
  created timestamptz DEFAULT now(),
  updated timestamptz DEFAULT now()
);
GRANT ALL on iembot_twitter_oauth to nobody,apache;

CREATE TABLE iembot_twitter_subs(
  user_id bigint REFERENCES iembot_twitter_oauth(user_id),
  screen_name varchar(128),
  channel varchar(64)
);
CREATE UNIQUE index iembot_twitter_subs_idx on 
 iembot_twitter_subs(screen_name, channel);
GRANT ALL on iembot_twitter_subs to nobody,apache;



---
--- IEMBot channels
---
CREATE TABLE iembot_channels(
  id varchar not null UNIQUE,
  name varchar,
  channel_key character varying DEFAULT substr(md5((random())::text), 0, 12)
);
GRANT all on iembot_channels to nobody,apache;

---
--- IEMBot rooms
---
CREATE TABLE iembot_room_subscriptions (
    roomname character varying(64),
    channel character varying(24)
);
CREATE UNIQUE index iembot_room_subscriptions_idx on
  iembot_room_subscriptions(roomname, channel);
GRANT all on iembot_room_subscriptions to nobody,apache;
---
--- IEMBot room subscriptions
---
CREATE TABLE iembot_rooms (
    roomname varchar(64),
    fbpage varchar,
    twitter varchar
);
GRANT all on iembot_rooms to nobody,apache;

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
  nexrad_product char(3),
  wtype varchar(32)
);
GRANT all on racoon_jobs to apache,nobody;



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
	cam varchar(11) UNIQUE,
	valid timestamp with time zone,
	drct smallint);
GRANT SELECT on camera_current to apache,nobody;
GRANT ALL on camera_current to mesonet,ldm;

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

--- Alias for pyWWA nwschat support
create view nwschat_properties as select * from properties;

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
	moviebase varchar,
	scrape_url varchar,
	is_vapix boolean,
	fullres varchar(9) DEFAULT '640x480' NOT NULL
	);
SELECT AddGeometryColumn('webcams', 'geom', 4326, 'POINT', 2);
GRANT all on webcams to mesonet,ldm;
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
	archive_begin timestamptz,
	archive_end timestamp with time zone,
	modified timestamp with time zone,
	tzname varchar(32),
	iemid SERIAL UNIQUE NOT NULL,
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
-- no commas in name please
alter table stations add constraint stations_nocommas check(strpos(name, ',') = 0);
CREATE UNIQUE index stations_idx on stations(id, network);
create UNIQUE index stations_iemid_idx on stations(iemid);
SELECT AddGeometryColumn('stations', 'geom', 4326, 'POINT', 2);
GRANT SELECT on stations to apache,nobody;
grant all on stations_iemid_seq to nobody,apache;
GRANT ALL on stations to mesonet,ldm;
GRANT ALL on stations_iemid_seq to mesonet,ldm;

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

-- Storage of station attributes
CREATE TABLE station_attributes(
	iemid int REFERENCES stations(iemid),
	attr varchar(128) NOT NULL,
  value varchar NOT NULL);
GRANT ALL on station_attributes to mesonet,ldm;
CREATE UNIQUE index station_attributes_idx on station_attributes(iemid, attr);
GRANT SELECT on station_attributes to nobody,apache;

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
  good smallint default 0,
  bad smallint default 0,
  abstain smallint default 0,
  voting boolean default true,
  tags varchar(1024),
  fbid bigint,
  appurl varchar(1024),
  javascripturl varchar(1024),
  views int default 0,
  mediasuffix varchar(8) DEFAULT 'png'
);
alter table feature SET WITH oids;
CREATE unique index feature_title_check_idx on feature(title);
CREATE index feature_valid_idx on feature(valid);
GRANT all on feature to nobody,apache;
GRANT all on feature to mesonet,ldm;

CREATE table shef_physical_codes(
  code char(2),
  name varchar(128),
  units varchar(64));
GRANT select on shef_physical_codes to apache,nobody;

CREATE table shef_duration_codes(
  code char(1),
  name varchar(128));
GRANT select on shef_duration_codes to apache,nobody;

CREATE table shef_extremum_codes(
  code char(1),
  name varchar(128));
GRANT select on shef_extremum_codes to apache,nobody;

-- Storage of metadata
CREATE TABLE iemrasters(
  id SERIAL UNIQUE,
  name varchar,
  description text,
  archive_start timestamptz,
  archive_end   timestamptz,
  units varchar(12),
  interval int,
  filename_template varchar,
  cf_long_name varchar
);
GRANT SELECT on iemrasters to nobody,apache;

-- Storage of color tables and values
CREATE TABLE iemrasters_lookup(
  iemraster_id int REFERENCES iemrasters(id),
  coloridx smallint,
  value real,
  r smallint,
  g smallint,
  b smallint
);
GRANT SELECT on iemrasters_lookup to nobody,apache;

-- Storage of IEM Dataset Metadata

CREATE TABLE iemdatasets(
  id serial UNIQUE,
  name varchar,
  description text,
  justification text,
  homepage varchar,
  alternatives varchar,
  archive_begin date,
  download text
);
GRANT ALL on iemdatasets to nobody,apache;
GRANT ALL on iemdatasets_id_seq to nobody,apache;

-- Storage of Autoplot timings and such
CREATE TABLE autoplot_timing(
	appid smallint NOT NULL,
	valid timestamptz NOT NULL,
	timing real NOT NULL,
	uri varchar,
	hostname varchar(24) NOT NULL);
GRANT SELECT on autoplot_timing to nobody,apache;
CREATE INDEX autoplot_timing_idx on autoplot_timing(appid);

-- Storage of talltowers analog request queue
CREATE TABLE talltowers_analog_queue
    (stations varchar(32),
    sts timestamptz,
    ets timestamptz,
    fmt varchar(32),
    email varchar(128),
    aff varchar(256),
    filled boolean DEFAULT 'f',
    valid timestamptz DEFAULT now());
GRANT ALL on talltowers_analog_queue to apache, mesonet;
