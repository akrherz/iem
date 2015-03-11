create table hourly_2015( 
  CONSTRAINT __hourly_2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2015_idx on hourly_2015(station, network, valid);
CREATE INDEX hourly_2015_valid_idx on hourly_2015(valid);
GRANT SELECT on hourly_2015 to nobody,apache;
CREATE RULE replace_hourly_2015 as 
    ON INSERT TO hourly_2015
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2015
          WHERE hourly_2015.station::text = new.station::text 
          AND hourly_2015.network::text = new.network::text 
          AND hourly_2015.valid = new.valid)) DO INSTEAD  
         UPDATE hourly_2015 SET phour = new.phour
  WHERE hourly_2015.station::text = new.station::text AND 
  hourly_2015.network::text = new.network::text AND 
  hourly_2015.valid = new.valid;

create table summary_2015( 
  CONSTRAINT __summary_2015_check 
  CHECK(day >= '2015-01-01'::date 
        and day < '2016-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2015_day_idx on summary_2015(day);
CREATE INDEX summary_2015_iemid_day_idx on summary_2015(iemid, day);
GRANT SELECT on summary_2015 to nobody,apache;
alter table summary_2015 alter max_tmpf set default -99;
alter table summary_2015 alter min_tmpf set default 99;
alter table summary_2015 alter max_sknt set default 0;
alter table summary_2015 alter max_gust set default 0;
alter table summary_2015 alter max_dwpf set default -99;
alter table summary_2015 alter min_dwpf set default 99;
alter table summary_2015 alter pday set default -99;
alter table summary_2015 alter pmonth set default -99;
alter table summary_2015 alter snoww set default -99;
alter table summary_2015 alter max_drct set default -99;
alter table summary_2015 
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE;

