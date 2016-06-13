-- Storage of baseline yield forecast data
CREATE TABLE yieldfx_baseline(
  station varchar(24),
  valid date,
  radn real,
  maxt real,
  mint real,
  rain real,
  windspeed real,
  rh real);
GRANT SELECT on yieldfx_baseline to nobody,apache;
