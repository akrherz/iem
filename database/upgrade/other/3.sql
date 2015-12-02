create table t2016( 
  CONSTRAINT __t2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_idx on t2016(station, valid);
GRANT SELECT on t2016 to nobody,apache;

create table flux2016( 
  CONSTRAINT __flux2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE INDEX flux2016_idx on flux2016(station, valid);
GRANT SELECT on flux2016 to nobody,apache;

CREATE TABLE hpd_2016(
        CONSTRAINT __hpd_2016_check
        CHECK(valid >= '2016-01-01 00:00+00'::timestamptz
              and valid < '2017-01-01 00:00+00'::timestamptz)
        )
        INHERITS (hpd_alldata);
GRANT SELECT on hpd_2016 to nobody,apache;
CREATE INDEX hpd_2016_station_idx on hpd_2016(station);

