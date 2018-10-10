DROP VIEW roads_view;
ALTER TABLE roads_base alter major type varchar(32);

CREATE TABLE roads_2018_2019_log(
  segid INT references roads_base(segid),
  valid timestamptz,
  cond_code smallint references roads_conditions(code),
  towing_prohibited bool,
  limited_vis bool,
  raw varchar);

GRANT ALL on roads_2018_2019_log to mesonet,ldm;
GRANT SELECT on roads_2018_2019_log to apache,nobody;
