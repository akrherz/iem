-- Storage of Nino Data
CREATE TABLE elnino(
	monthdate date UNIQUE,
	anom_34 real,
	soi_3m real
);
GRANT SELECT on elnino to nobody,apache;