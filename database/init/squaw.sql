
CREATE TABLE real_flow(
  gauge_id int,
  valid timestamptz,
  cfs int
);
CREATE INDEX real_flow_idx on real_flow(gauge_id, valid);

CREATE TABLE storms(
  id SERIAL UNIQUE,
  name varchar,
  created timestamptz,
  edited timestamptz,
  notes text
);

CREATE TABLE events(
  storm_id int REFERENCES storms(id),
  basin_id smallint,
  precip real,
  onset timestamptz,
  duration real
);
CREATE UNIQUE index events_idx on events(storm_id, basin_id);

CREATE TABLE scenarios(
  id SERIAL UNIQUE,
  name varchar,
  created timestamptz,
  edited timestamptz,
  notes text);

CREATE TABLE scenario_events(
  scenario_id int REFERENCES scenarios(id),
  basin_id smallint,
  precip real,
  onset timestamptz,
  duration real);