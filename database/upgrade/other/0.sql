create table t2015( 
  CONSTRAINT __t2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_idx on t2015(station, valid);
GRANT SELECT on t2015 to nobody,apache;

create table flux2015( 
  CONSTRAINT __flux2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2015_idx on flux2015(station, valid);
GRANT SELECT on flux2015 to nobody,apache;
