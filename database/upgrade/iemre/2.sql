-- _______________________________________________________________________
-- Storage of CFS forecast
CREATE TABLE iemre_daily_forecast(
    gid int REFERENCES iemre_grid(gid),
    valid date,
    high_tmpk real,
    low_tmpk real,
    p01d real,
    rsds real
);
ALTER TABLE iemre_daily_forecast OWNER to mesonet;
GRANT ALL on iemre_daily_forecast to mesonet,ldm;
GRANT SELECT on iemre_daily_forecast to nobody,apache;

CREATE INDEX on iemre_daily_forecast(valid);
CREATE INDEX on iemre_daily_forecast(gid);
