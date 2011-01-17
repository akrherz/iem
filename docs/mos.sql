---
--- Not sure why, just something to hold a curiousity of large MOS differences
---
CREATE TABLE large_difference(
  model varchar(5),
  valid timestamp with time zone,
  station varchar(5),
  ob real,
  mos real);
GRANT SELECT on large_difference to nobody,apache;