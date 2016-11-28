create table model_gridpoint_2017( 
  CONSTRAINT __model_gridpoint_2017_check 
  CHECK(runtime >= '2017-01-01 00:00+00'::timestamptz 
        and runtime < '2018-01-01 00:00+00'::timestamptz)) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2017_idx 
	on model_gridpoint_2017(station, model, runtime);
GRANT SELECT on model_gridpoint_2017 to nobody,apache;

create table t2017( 
  CONSTRAINT __t2017_check 
  CHECK(runtime >= '2017-01-01 00:00+00'::timestamptz 
        and runtime < '2018-01-01 00:00+00'::timestamptz)) 
  INHERITS (alldata);
CREATE INDEX t2017_idx on t2017(station, model, runtime);
CREATE INDEX t2017_runtime_idx on t2017(runtime);
GRANT SELECT on t2017 to nobody,apache;