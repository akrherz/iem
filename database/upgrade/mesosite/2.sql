-- Store IEM Raster metadata, remove my previous tables on this matter

DROP TABLE raster_lookup;
DROP TABLE raster_metadata;

-- Storage of metadata
CREATE TABLE iemrasters(
  id SERIAL UNIQUE,
  name varchar,
  description text,
  archive_start timestamptz,
  archive_end   timestamptz,
  units varchar(12),
  interval int
);
GRANT SELECT on iemrasters to nobody,apache;

-- Storage of color tables and values
CREATE TABLE iemrasters_lookup(
  iemraster_id int REFERENCES iemrasters(id),
  coloridx smallint,
  value real,
  r smallint,
  g smallint,
  b smallint
);
GRANT SELECT on iemrasters_lookup to nobody,apache;