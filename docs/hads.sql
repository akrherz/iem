CREATE TABLE raw2010(
	station varchar(8),
	valid timestamp with time zone,
	key varchar(8),
	value real
);

CREATE TABLE raw2010_12() inherits (raw2010);

CREATE TABLE unknown(
	nwsli varchar(8),
	product varchar(64),
	network varchar(24),
);