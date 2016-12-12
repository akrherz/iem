ALTER TABLE stations ADD CONSTRAINT stations_iemid UNIQUE (iemid);

-- Storage of station attributes
CREATE TABLE station_attributes(
	iemid int REFERENCES stations(iemid),
	attr varchar(128) NOT NULL);
CREATE UNIQUE index station_attributes_idx on station_attributes(iemid, attr);
GRANT SELECT on station_attributes to nobody,apache;
