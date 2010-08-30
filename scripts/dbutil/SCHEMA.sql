CREATE TABLE stations(
 id varchar(20),
 synop int,
 name varchar(40),
 state char(2),
 country char(2),
 elevation real,
 network varchar(20),
 online boolean,
 params varchar(300),
 county varchar(50),
 plot_name varchar(40),
 climate_site varchar(6),
 remote_id int,
 wfo char(3),
 archive_begin timestamp with time zone,
 archive_end timestamp with time zone
);

SELECT addgeometrycolumn('stations', 'geom', 4326, 'POINT', 2);

GRANT SELECT on stations to nobody,apache;
