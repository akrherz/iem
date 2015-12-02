create table model_gridpoint_2016( 
  CONSTRAINT __model_gridpoint_2016_check 
  CHECK(runtime >= '2016-01-01 00:00+00'::timestamptz 
        and runtime < '2017-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2016_idx 
	on model_gridpoint_2016(station, model, runtime);
GRANT SELECT on model_gridpoint_2016 to nobody,apache;

create table t2016( 
  CONSTRAINT __t2016_check 
  CHECK(runtime >= '2016-01-01 00:00+00'::timestamptz 
        and runtime < '2017-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2016_idx on t2016(station, model, runtime);
CREATE INDEX t2016_runtime_idx on t2016(runtime);
GRANT SELECT on t2016 to nobody,apache;
