---
--- Store the climate normals
---
CREATE TABLE climate81(
  station varchar(6),
  valid date,
  high real,
  low real,
  precip real,
  snow real,
  max_high real,
  max_low real,
  min_high real,
  min_low real,
  max_precip real,
  years int,
  gdd50 real,
  sdd86 real,
  max_high_yr   int,
  max_low_yr    int,
  min_high_yr   int,
  min_low_yr    int,
  max_precip_yr int,
  max_range     smallint,
  min_range smallint 
);
CREATE UNIQUE INDEX climate81_idx on climate81(station,valid);
GRANT SELECT on climate81 to nobody,apache;

CREATE FUNCTION gdd48(real, real) RETURNS numeric
    LANGUAGE sql
    AS $_$select (( (CASE WHEN $1 > 48 THEN (case when $1 > 86 THEN 86 ELSE $1 END ) - 48 ELSE 0 END) + (CASE WHEN $2 > 48 THEN $2 - 48 ELSE 0 END) ) / 2.0)::numeric$_$;

--
-- base, max, high, low
 CREATE FUNCTION gddXX(real, real, real, real) RETURNS numeric
    LANGUAGE sql
    AS $_$select (( (CASE WHEN $3 > $1 THEN (case when $3 > $2 THEN $2 ELSE $3 END ) - $1 ELSE 0 END) + 
    (CASE WHEN $4 > $1 THEN $4 - $1 ELSE 0 END) ) / 2.0)::numeric$_$;
 