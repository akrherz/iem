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
	ugc_zone char(6)
);
CREATE UNIQUE index stations_idx on stations(id, network);
create index stations_iemid_idx on stations(iemid);
SELECT AddGeometryColumn('stations', 'geom', 4326, 'POINT', 2);
GRANT SELECT on stations to apache,nobody;
grant all on stations_iemid_seq to nobody,apache;

CREATE TABLE alldata(
 station        character varying(4)  ,    
 valid          timestamp with time zone  ,
 tmpf           real            ,          
 dwpf           real            ,          
 drct           real              ,        
 sknt           real             ,         
 alti           real                ,      
 gust           real               ,       
 vsby           real                ,      
 skyc1          character(3)         ,     
 skyc2          character(3)          ,    
 skyc3          character(3)           ,   
 skyl1          integer                 ,  
 skyl2          integer                  , 
 skyl3          integer                   ,
 metar          character varying(256)    ,
 skyc4          character(3)              ,
 skyl4          integer                   ,
 p03i           real                      ,
 p06i           real                      ,
 p24i           real                      ,
 max_tmpf_6hr   real                      ,
 min_tmpf_6hr   real                      ,
 max_tmpf_24hr  real                      ,
 min_tmpf_24hr  real                      ,
 mslp           real                      ,
 p01i           real                      ,
 presentwx     character varying(24)     
);

CREATE TABLE t2012 () inherits (alldata);

---
---
---
create table t2014( 
  CONSTRAINT __t2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_station_idx on t2014(station);
CREATE INDEX t2014_valid_idx on t2014(valid);
GRANT SELECT on t2014 to nobody,apache;

create table t2014_1minute( 
  CONSTRAINT __t2014_1minute_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata_1minute);
CREATE INDEX t2014_1minte_station_idx on t2014_1minute(station);
CREATE INDEX t2014_1minute_valid_idx on t2014_1minute(valid);
GRANT SELECT on t2014_1minute to nobody,apache;