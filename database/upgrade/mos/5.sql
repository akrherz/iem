create table model_gridpoint_2019(
  CONSTRAINT __model_gridpoint_2019_check
  CHECK(runtime >= '2019-01-01 00:00+00'::timestamptz
        and runtime < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2019_idx
        on model_gridpoint_2019(station, model, runtime);
GRANT SELECT on model_gridpoint_2019 to nobody,apache;

create table t2019(
  CONSTRAINT __t2019_check
  CHECK(runtime >= '2019-01-01 00:00+00'::timestamptz
        and runtime < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2019_idx on t2019(station, model, runtime);
CREATE INDEX t2019_runtime_idx on t2019(runtime);
GRANT SELECT on t2019 to nobody,apache;
