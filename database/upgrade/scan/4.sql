create table t1983_hourly( 
  CONSTRAINT __t1983_hourly_check
  CHECK(valid >= '1983-01-01 00:00+00'::timestamptz
        and valid < '1984-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1983_hourly_idx on t1983_hourly(station, valid);
GRANT SELECT on t1983_hourly to nobody,apache;
GRANT ALL on t1983_hourly to mesonet,ldm;
    

create table t1984_hourly( 
  CONSTRAINT __t1984_hourly_check
  CHECK(valid >= '1984-01-01 00:00+00'::timestamptz
        and valid < '1985-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1984_hourly_idx on t1984_hourly(station, valid);
GRANT SELECT on t1984_hourly to nobody,apache;
GRANT ALL on t1984_hourly to mesonet,ldm;
    

create table t1985_hourly( 
  CONSTRAINT __t1985_hourly_check
  CHECK(valid >= '1985-01-01 00:00+00'::timestamptz
        and valid < '1986-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1985_hourly_idx on t1985_hourly(station, valid);
GRANT SELECT on t1985_hourly to nobody,apache;
GRANT ALL on t1985_hourly to mesonet,ldm;
    

create table t1986_hourly( 
  CONSTRAINT __t1986_hourly_check
  CHECK(valid >= '1986-01-01 00:00+00'::timestamptz
        and valid < '1987-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1986_hourly_idx on t1986_hourly(station, valid);
GRANT SELECT on t1986_hourly to nobody,apache;
GRANT ALL on t1986_hourly to mesonet,ldm;
    

create table t1987_hourly( 
  CONSTRAINT __t1987_hourly_check
  CHECK(valid >= '1987-01-01 00:00+00'::timestamptz
        and valid < '1988-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1987_hourly_idx on t1987_hourly(station, valid);
GRANT SELECT on t1987_hourly to nobody,apache;
GRANT ALL on t1987_hourly to mesonet,ldm;
    

create table t1988_hourly( 
  CONSTRAINT __t1988_hourly_check
  CHECK(valid >= '1988-01-01 00:00+00'::timestamptz
        and valid < '1989-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1988_hourly_idx on t1988_hourly(station, valid);
GRANT SELECT on t1988_hourly to nobody,apache;
GRANT ALL on t1988_hourly to mesonet,ldm;
    

create table t1989_hourly( 
  CONSTRAINT __t1989_hourly_check
  CHECK(valid >= '1989-01-01 00:00+00'::timestamptz
        and valid < '1990-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1989_hourly_idx on t1989_hourly(station, valid);
GRANT SELECT on t1989_hourly to nobody,apache;
GRANT ALL on t1989_hourly to mesonet,ldm;
    

create table t1990_hourly( 
  CONSTRAINT __t1990_hourly_check
  CHECK(valid >= '1990-01-01 00:00+00'::timestamptz
        and valid < '1991-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1990_hourly_idx on t1990_hourly(station, valid);
GRANT SELECT on t1990_hourly to nobody,apache;
GRANT ALL on t1990_hourly to mesonet,ldm;
    

create table t1991_hourly( 
  CONSTRAINT __t1991_hourly_check
  CHECK(valid >= '1991-01-01 00:00+00'::timestamptz
        and valid < '1992-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1991_hourly_idx on t1991_hourly(station, valid);
GRANT SELECT on t1991_hourly to nobody,apache;
GRANT ALL on t1991_hourly to mesonet,ldm;
    

create table t1992_hourly( 
  CONSTRAINT __t1992_hourly_check
  CHECK(valid >= '1992-01-01 00:00+00'::timestamptz
        and valid < '1993-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1992_hourly_idx on t1992_hourly(station, valid);
GRANT SELECT on t1992_hourly to nobody,apache;
GRANT ALL on t1992_hourly to mesonet,ldm;
    

create table t1993_hourly( 
  CONSTRAINT __t1993_hourly_check
  CHECK(valid >= '1993-01-01 00:00+00'::timestamptz
        and valid < '1994-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1993_hourly_idx on t1993_hourly(station, valid);
GRANT SELECT on t1993_hourly to nobody,apache;
GRANT ALL on t1993_hourly to mesonet,ldm;
    

create table t1994_hourly( 
  CONSTRAINT __t1994_hourly_check
  CHECK(valid >= '1994-01-01 00:00+00'::timestamptz
        and valid < '1995-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1994_hourly_idx on t1994_hourly(station, valid);
GRANT SELECT on t1994_hourly to nobody,apache;
GRANT ALL on t1994_hourly to mesonet,ldm;
    

create table t1995_hourly( 
  CONSTRAINT __t1995_hourly_check
  CHECK(valid >= '1995-01-01 00:00+00'::timestamptz
        and valid < '1996-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1995_hourly_idx on t1995_hourly(station, valid);
GRANT SELECT on t1995_hourly to nobody,apache;
GRANT ALL on t1995_hourly to mesonet,ldm;
    

create table t1996_hourly( 
  CONSTRAINT __t1996_hourly_check
  CHECK(valid >= '1996-01-01 00:00+00'::timestamptz
        and valid < '1997-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1996_hourly_idx on t1996_hourly(station, valid);
GRANT SELECT on t1996_hourly to nobody,apache;
GRANT ALL on t1996_hourly to mesonet,ldm;
    

create table t1997_hourly( 
  CONSTRAINT __t1997_hourly_check
  CHECK(valid >= '1997-01-01 00:00+00'::timestamptz
        and valid < '1998-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1997_hourly_idx on t1997_hourly(station, valid);
GRANT SELECT on t1997_hourly to nobody,apache;
GRANT ALL on t1997_hourly to mesonet,ldm;
    

create table t1998_hourly( 
  CONSTRAINT __t1998_hourly_check
  CHECK(valid >= '1998-01-01 00:00+00'::timestamptz
        and valid < '1999-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1998_hourly_idx on t1998_hourly(station, valid);
GRANT SELECT on t1998_hourly to nobody,apache;
GRANT ALL on t1998_hourly to mesonet,ldm;
    

create table t1999_hourly( 
  CONSTRAINT __t1999_hourly_check
  CHECK(valid >= '1999-01-01 00:00+00'::timestamptz
        and valid < '2000-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t1999_hourly_idx on t1999_hourly(station, valid);
GRANT SELECT on t1999_hourly to nobody,apache;
GRANT ALL on t1999_hourly to mesonet,ldm;
