-- initial definition was not range partitioned, so we have to a convoluted
-- dance
ALTER TABLE alldata RENAME to alldata_old;
ALTER TABLE alldata_1minute RENAME to alldata_1minute_old;

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
) PARTITION by RANGE (valid);
ALTER TABLE alldata OWNER to mesonet;
GRANT ALL on alldata to ldm;
GRANT SELECT on alldata to nobody,apache;

do
$do$
declare
     year int;
begin
    for year in 1928..2019
    loop
        execute format($f$
            ALTER TABLE t%s NO INHERIT alldata_old
            $f$, year);
        execute format($f$
            ALTER TABLE alldata ATTACH PARTITION t%s
            FOR VALUES FROM ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
        $f$, year, year, year + 1);
    end loop;
end;
$do$;

do
$do$
declare
     year int;
begin
    for year in 2020..2030
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

DROP TABLE alldata_old;

-- ____________________________

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
     month int;
     mytable varchar;
begin
    for year in 2000..2019
    loop
        execute format($f$
            ALTER TABLE t%s_1minute NO INHERIT alldata_1minute_old
            $f$, year);
        execute format($f$
            ALTER TABLE alldata_1minute ATTACH PARTITION t%s_1minute
            FOR VALUES FROM ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
        $f$, year, year, year + 1);
    end loop;
end;
$do$;


do
$do$
declare
     year int;
begin
    for year in 2020..2030
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
            CREATE INDEX t%s_1minute_valid_idx on t%s_1minute(valid)
        $f$, year, year);
        execute format($f$
            CREATE INDEX t%s_1minute_station_idx on t%s_1minute(station)
        $f$, year, year);
    end loop;
end;
$do$;

DROP TABLE alldata_1minute_old;
