CREATE TABLE roads_2015_log(
  segid int,
  valid timestamptz,
  cond_code smallint,
  towing_prohibited boolean,
  limited_vis boolean,
  raw varchar);
GRANT SELECT on roads_2015_log to nobody,apache;