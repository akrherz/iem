-- Storage of Autoplot timings and such
CREATE TABLE autoplot_timing(
	appid smallint NOT NULL,
	valid timestamptz NOT NULL,
	timing real NOT NULL,
	uri varchar,
	hostname varchar(24) NOT NULL);
GRANT SELECT on autoplot_timing to nobody,apache;
CREATE INDEX autoplot_timing_idx on autoplot_timing(appid);
