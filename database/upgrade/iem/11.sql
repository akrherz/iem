-- Create the 2017 tables while we are messing around here
create table hourly_2017(
  CONSTRAINT __hourly_2017_check
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
        and valid < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (hourly);
CREATE INDEX hourly_2017_idx on hourly_2017(station, network, valid);
CREATE INDEX hourly_2017_valid_idx on hourly_2017(valid);
GRANT SELECT on hourly_2017 to nobody,apache;
CREATE RULE replace_hourly_2017 as
    ON INSERT TO hourly_2017
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2017
          WHERE hourly_2017.station::text = new.station::text
          AND hourly_2017.network::text = new.network::text
          AND hourly_2017.valid = new.valid)) DO INSTEAD
         UPDATE hourly_2017 SET phour = new.phour
  WHERE hourly_2017.station::text = new.station::text AND
  hourly_2017.network::text = new.network::text AND
  hourly_2017.valid = new.valid;

create table summary_2017(
  CONSTRAINT __summary_2017_check
  CHECK(day >= '2017-01-01'::date
        and day < '2018-01-01'::date))
  INHERITS (summary);
CREATE INDEX summary_2017_day_idx on summary_2017(day);
CREATE UNIQUE INDEX summary_2017_iemid_day_idx on summary_2017(iemid, day);
GRANT SELECT on summary_2017 to nobody,apache;
alter table summary_2017
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE;
