create table t2018(
  CONSTRAINT __t2018_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2018_idx on t2018(station, valid);
GRANT SELECT on t2018 to nobody,apache;

create table flux2018(
  CONSTRAINT __flux2018_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2018_idx on flux2018(station, valid);
GRANT SELECT on flux2018 to nobody,apache;

CREATE TABLE hpd_2018(
        CONSTRAINT __hpd_2018_check
        CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
              and valid < '2019-01-01 00:00+00'::timestamptz)
        )
        INHERITS (hpd_alldata);
GRANT SELECT on hpd_2018 to nobody,apache;
CREATE INDEX hpd_2018_station_idx on hpd_2018(station);
