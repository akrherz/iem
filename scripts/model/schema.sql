CREATE TABLE model_gridpoint(
  station varchar(4),
  model   varchar(12),
  runtime timestamp with time zone,
  ftime   timestamp with time zone,
  sbcape  real,
  sbcin   real,
  lhflux  real,
  pwater  real
);

GRANT SELECT on model_gridpoint to nobody,apache;

CREATE TABLE model_gridpoint_2010() INHERITS (model_gridpoint);
CREATE INDEX model_gridpoint_2010_idx on 
  model_gridpoint_2010(station, model, runtime);
GRANT SELECT on model_gridpoint_2010 to nobody,apache;
