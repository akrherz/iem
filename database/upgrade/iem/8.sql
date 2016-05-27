-- Issue #54, remove hacky 99 and -99 usage
DO $$
DECLARE
  rec record;
BEGIN
FOR rec in SELECT generate_series(1941, 2015) as year LOOP
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN max_tmpf DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET max_tmpf = null WHERE max_tmpf = -99';
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN min_tmpf DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET min_tmpf = null WHERE min_tmpf = 99';
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN max_dwpf DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET max_dwpf = null WHERE max_dwpf = -99';
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN min_dwpf DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET min_dwpf = null WHERE min_dwpf = 99';
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN pday DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET pday = null WHERE pday = -99';
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN pmonth DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET pmonth = null WHERE pmonth = -99';
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN max_drct DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET max_drct = null WHERE max_drct = -99';
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN max_srad DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET max_srad = null WHERE max_srad = -99';
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN max_sknt DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET max_sknt = null WHERE max_sknt = -99';
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN max_gust DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET max_gust = null WHERE max_gust = -99';
  EXECUTE 'ALTER TABLE summary_'|| rec.year || ' ALTER COLUMN snoww DROP DEFAULT';
  EXECUTE 'UPDATE summary_'|| rec.year || ' SET snoww = null WHERE snoww = -99';
END LOOP;
END$$;


-- Create the 2016 tables while we are messing around here
create table hourly_2016( 
  CONSTRAINT __hourly_2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (hourly);
CREATE INDEX hourly_2016_idx on hourly_2016(station, network, valid);
CREATE INDEX hourly_2016_valid_idx on hourly_2016(valid);
GRANT SELECT on hourly_2016 to nobody,apache;
CREATE RULE replace_hourly_2016 as 
    ON INSERT TO hourly_2016
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2016
          WHERE hourly_2016.station::text = new.station::text 
          AND hourly_2016.network::text = new.network::text 
          AND hourly_2016.valid = new.valid)) DO INSTEAD  
         UPDATE hourly_2016 SET phour = new.phour
  WHERE hourly_2016.station::text = new.station::text AND 
  hourly_2016.network::text = new.network::text AND 
  hourly_2016.valid = new.valid;

create table summary_2016( 
  CONSTRAINT __summary_2016_check 
  CHECK(day >= '2016-01-01'::date 
        and day < '2017-01-01'::date)) 
  INHERITS (summary);
CREATE INDEX summary_2016_day_idx on summary_2016(day);
CREATE UNIQUE INDEX summary_2016_iemid_day_idx on summary_2016(iemid, day);
GRANT SELECT on summary_2016 to nobody,apache;
alter table summary_2016 
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE;