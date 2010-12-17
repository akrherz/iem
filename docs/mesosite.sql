CREATE TABLE stations(
	id varchar(20),
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
	wfo varchar(3),
	archive_begin timestamp with time zone,
	archive_end timestamp with time zone
);
CREATE UNIQUE index stations_idx on stations(id, network);
SELECT AddGeometryColumn('stations', 'geom', 4326, 'POINT', 2);
GRANT SELECT on stations to apache,nobody;

---
create table iemmaps(
  id SERIAL,
  title varchar(256),
  entered timestamp with time zone DEFAULT now(),
  description text,
  keywords varchar(256),
  views int,
  ref varchar(32),
  category varchar(24)
);
GRANT all on iemmaps to apache,nobody;
GRANT all on iemmaps_id_seq to apache,nobody;
