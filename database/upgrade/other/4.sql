create table t2017( 
  CONSTRAINT __t2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00'::timestamptz)) 
  INHERITS (alldata);
CREATE INDEX t2017_idx on t2017(station, valid);
GRANT SELECT on t2017 to nobody,apache;

create table flux2017( 
  CONSTRAINT __flux2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00'::timestamptz)) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2017_idx on flux2017(station, valid);
GRANT SELECT on flux2017 to nobody,apache;

CREATE TABLE hpd_2017(
        CONSTRAINT __hpd_2017_check
        CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
              and valid < '2018-01-01 00:00+00'::timestamptz)
        )
        INHERITS (hpd_alldata);
GRANT SELECT on hpd_2017 to nobody,apache;
CREATE INDEX hpd_2017_station_idx on hpd_2017(station);

