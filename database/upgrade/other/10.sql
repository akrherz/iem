create table uscrn_t2019(
  CONSTRAINT __t2019_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'))
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2019_station_idx on uscrn_t2019(station);
CREATE INDEX uscrn_t2019_valid_idx on uscrn_t2019(valid);
GRANT SELECT on uscrn_t2019 to nobody,apache;
GRANT ALL on uscrn_t2019 to ldm,mesonet;
