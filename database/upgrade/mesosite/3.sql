-- Storage of IEM Dataset Metadata

CREATE TABLE iemdatasets(
  id serial UNIQUE,
  name varchar,
  description text,
  justification text,
  homepage varchar,
  alternatives varchar,
  archive_begin date,
  download text
);
GRANT SELECT on iemdatasets to nobody,apache;