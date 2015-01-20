--
-- Storage of PIREPs
--
CREATE TABLE pireps(
  valid timestamptz,
  geom geography(POINT,4326),
  is_urgent boolean,
  aircraft_type varchar,
  report varchar
);
CREATE INDEX pireps_valid_idx on pireps(valid);
GRANT SELECT on pireps to nobody,apache;