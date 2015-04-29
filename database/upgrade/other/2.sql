-- Storage of ncdc HPD data
--
CREATE TABLE hpd_alldata(
  station varchar(6),
  valid timestamptz,
  counter real,
  tmpc real,
  battery real,
  calc_precip real
);
GRANT SELECT on hpd_alldata to nobody,apache;

-- Individual years
CREATE TABLE hpd_2009(
	CONSTRAINT __hpd_2009_check
	CHECK(valid >= '2009-01-01 00:00+00'::timestamptz
	      and valid < '2010-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2009 to nobody,apache;
CREATE INDEX hpd_2009_station_idx on hpd_2009(station);

CREATE TABLE hpd_2010(
	CONSTRAINT __hpd_2010_check
	CHECK(valid >= '2010-01-01 00:00+00'::timestamptz
	      and valid < '2011-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2010 to nobody,apache;
CREATE INDEX hpd_2010_station_idx on hpd_2010(station);

CREATE TABLE hpd_2011(
	CONSTRAINT __hpd_2011_check
	CHECK(valid >= '2011-01-01 00:00+00'::timestamptz
	      and valid < '2012-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2011 to nobody,apache;
CREATE INDEX hpd_2011_station_idx on hpd_2011(station);

CREATE TABLE hpd_2012(
	CONSTRAINT __hpd_2012_check
	CHECK(valid >= '2012-01-01 00:00+00'::timestamptz
	      and valid < '2013-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2012 to nobody,apache;
CREATE INDEX hpd_2012_station_idx on hpd_2012(station);

CREATE TABLE hpd_2013(
	CONSTRAINT __hpd_2013_check
	CHECK(valid >= '2013-01-01 00:00+00'::timestamptz
	      and valid < '2014-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2013 to nobody,apache;
CREATE INDEX hpd_2013_station_idx on hpd_2013(station);

CREATE TABLE hpd_2014(
	CONSTRAINT __hpd_2014_check
	CHECK(valid >= '2014-01-01 00:00+00'::timestamptz
	      and valid < '2015-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2014 to nobody,apache;
CREATE INDEX hpd_2014_station_idx on hpd_2014(station);

CREATE TABLE hpd_2015(
	CONSTRAINT __hpd_2015_check
	CHECK(valid >= '2015-01-01 00:00+00'::timestamptz
	      and valid < '2016-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2015 to nobody,apache;
CREATE INDEX hpd_2015_station_idx on hpd_2015(station);
