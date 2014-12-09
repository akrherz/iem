create table model_gridpoint_2015( 
  CONSTRAINT __model_gridpoint_2015_check 
  CHECK(runtime >= '2015-01-01 00:00+00'::timestamptz 
        and runtime < '2016-01-01 00:00+00')) 
  INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2015_idx 
	on model_gridpoint_2015(station, model, runtime);
GRANT SELECT on model_gridpoint_2015 to nobody,apache;

create table t2015( 
  CONSTRAINT __t2015_check 
  CHECK(runtime >= '2015-01-01 00:00+00'::timestamptz 
        and runtime < '2016-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2015_idx on t2015(station, model, runtime);
CREATE INDEX t2015_runtime_idx on t2015(runtime);
GRANT SELECT on t2015 to nobody,apache;
