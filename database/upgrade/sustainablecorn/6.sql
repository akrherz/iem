-- Storage of weather data
CREATE TABLE weather_data_daily(
  station varchar(32),
  valid date,
  high real,
  low real,
  precip real);
GRANT SELECT on weather_data_daily to nobody,apache;
CREATE INDEX weather_data_daily_idx on weather_data_daily(station, valid);

CREATE TABLE weather_data_obs(
  station varchar(32),
  valid timestamptz,
  tmpf real,
  dwpf real,
  drct real,
  sknt real);
GRANT SELECT on weather_data_obs to nobody,apache;
CREATE INDEX weather_data_obs_idx on weather_data_obs(station, valid);

ALTER TABLE soil_data ADD sampledate date;
ALTER TABLE soil_data_log ADD sampledate date;