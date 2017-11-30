create table model_gridpoint_2018(
  CONSTRAINT __model_gridpoint_2018_check
  CHECK(runtime >= '2018-01-01 00:00+00'::timestamptz
        and runtime < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2018_idx
        on model_gridpoint_2018(station, model, runtime);
GRANT SELECT on model_gridpoint_2018 to nobody,apache;

create table t2018(
  CONSTRAINT __t2018_check
  CHECK(runtime >= '2018-01-01 00:00+00'::timestamptz
        and runtime < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2018_idx on t2018(station, model, runtime);
CREATE INDEX t2018_runtime_idx on t2018(runtime);
GRANT SELECT on t2018 to nobody,apache;
