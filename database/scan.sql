CREATE TABLE alldata(
	station varchar(5),
	valid timestamptz,
	tmpf real,
	dwpf real,
	srad real,
	sknt real,
	relh real,
	pres real,
	c1tmpf real,
	c2tmpf real,
	c3tmpf real,
	c4tmpf real,
	c5tmpf real,
	c1smv real,
	c2smv real,
	c3smv real,
	c4smv real,
	c5smv real,
	phour real
);
GRANT SELECT on alldata to nobody,apache;

create table t2013_hourly( 
  CONSTRAINT __t2013_hourly_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_hourly_idx on t2013_hourly(station, valid);
GRANT SELECT on t2013_hourly to nobody,apache;

create table t2014_hourly( 
  CONSTRAINT __t2014_hourly_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_hourly_idx on t2014_hourly(station, valid);
GRANT SELECT on t2014_hourly to nobody,apache;