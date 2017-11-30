-- Create the 2018 tables while we are messing around here
create table hourly_2018(
  CONSTRAINT __hourly_2018_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (hourly);
CREATE INDEX hourly_2018_idx on hourly_2018(station, network, valid);
CREATE INDEX hourly_2018_valid_idx on hourly_2018(valid);
GRANT SELECT on hourly_2018 to nobody,apache;
CREATE RULE replace_hourly_2018 as
    ON INSERT TO hourly_2018
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2018
          WHERE hourly_2018.station::text = new.station::text
          AND hourly_2018.network::text = new.network::text
          AND hourly_2018.valid = new.valid)) DO INSTEAD
         UPDATE hourly_2018 SET phour = new.phour
  WHERE hourly_2018.station::text = new.station::text AND
  hourly_2018.network::text = new.network::text AND
  hourly_2018.valid = new.valid;

create table summary_2018(
  CONSTRAINT __summary_2018_check
  CHECK(day >= '2018-01-01'::date
        and day < '2019-01-01'::date))
  INHERITS (summary);
CREATE INDEX summary_2018_day_idx on summary_2018(day);
CREATE UNIQUE INDEX summary_2018_iemid_day_idx on summary_2018(iemid, day);
GRANT SELECT on summary_2018 to nobody,apache;
alter table summary_2018
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE;
  