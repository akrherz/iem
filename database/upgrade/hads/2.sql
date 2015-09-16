-- Need a faster storage for inbound data, adding it to tables with indexes
-- was too expensive
CREATE TABLE raw_inbound(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);
CREATE TABLE raw_inbound_tmp(
	station varchar(8),
	valid timestamptz,
	key varchar(11),
	value real
);