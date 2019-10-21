-- Storage of MCDs
CREATE TABLE mcd(
    product_id varchar(32),
    geom geometry(Polygon,4326),
    product text,
    year int NOT NULL,
    num int NOT NULL,
    issue timestamptz,
    expire timestamptz,
    watch_confidence smallint
);
ALTER TABLE mcd OWNER to mesonet;
GRANT ALL on mcd to ldm;
GRANT SELECT on mcd to nobody;

CREATE INDEX ON mcd(issue);
CREATE INDEX ON mcd(num);
CREATE INDEX mcd_geom_index on mcd USING GIST(geom);

-- Storage of MPDs
CREATE TABLE mpd(
    product_id varchar(32),
    geom geometry(Polygon,4326),
    product text,
    year int NOT NULL,
    num int NOT NULL,
    issue timestamptz,
    expire timestamptz,
    watch_confidence smallint
);
ALTER TABLE mpd OWNER to mesonet;
GRANT ALL on mpd to ldm;
GRANT SELECT on mpd to nobody;

CREATE INDEX ON mpd(issue);
CREATE INDEX ON mpd(num);
CREATE INDEX mpd_geom_index on mpd USING GIST(geom);
