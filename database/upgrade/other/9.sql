create table t2019(
  CONSTRAINT __t2019_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2019_idx on t2019(station, valid);
GRANT SELECT on t2019 to nobody,apache;

create table flux2019(
  CONSTRAINT __flux2019_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2019_idx on flux2019(station, valid);
GRANT SELECT on flux2019 to nobody,apache;

CREATE TABLE hpd_2019(
        CONSTRAINT __hpd_2019_check
        CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
              and valid < '2020-01-01 00:00+00'::timestamptz)
        )
        INHERITS (hpd_alldata);
GRANT SELECT on hpd_2019 to nobody,apache;
CREATE INDEX hpd_2019_station_idx on hpd_2019(station);
