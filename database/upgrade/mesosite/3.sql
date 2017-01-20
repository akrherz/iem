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
GRANT ALL on iemdatasets to nobody,apache;
GRANT ALL on iemdatasets_id_seq to nobody,apache;
