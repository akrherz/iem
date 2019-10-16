CREATE TABLE roads_2019_2020_log(
  segid INT references roads_base(segid),
  valid timestamptz,
  cond_code smallint references roads_conditions(code),
  towing_prohibited bool,
  limited_vis bool,
  raw varchar);

GRANT ALL on roads_2019_2020_log to mesonet,ldm;
GRANT SELECT on roads_2019_2020_log to apache,nobody;
