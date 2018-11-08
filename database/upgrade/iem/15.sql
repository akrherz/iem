-- Create the 2019 tables while we are messing around here
create table hourly_2019(
  CONSTRAINT __hourly_2019_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (hourly);
CREATE INDEX hourly_2019_idx on hourly_2019(station, network, valid);
CREATE INDEX hourly_2019_valid_idx on hourly_2019(valid);
GRANT SELECT on hourly_2019 to nobody,apache;
CREATE RULE replace_hourly_2019 as
    ON INSERT TO hourly_2019
   WHERE (EXISTS ( SELECT 1
           FROM hourly_2019
          WHERE hourly_2019.station::text = new.station::text
          AND hourly_2019.network::text = new.network::text
          AND hourly_2019.valid = new.valid)) DO INSTEAD
         UPDATE hourly_2019 SET phour = new.phour
  WHERE hourly_2019.station::text = new.station::text AND
  hourly_2019.network::text = new.network::text AND
  hourly_2019.valid = new.valid;

create table summary_2019(
  CONSTRAINT __summary_2019_check
  CHECK(day >= '2019-01-01'::date
        and day < '2020-01-01'::date))
  INHERITS (summary);
CREATE INDEX summary_2019_day_idx on summary_2019(day);
CREATE UNIQUE INDEX summary_2019_iemid_day_idx on summary_2019(iemid, day);
GRANT SELECT on summary_2019 to nobody,apache;
alter table summary_2019
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE;
  