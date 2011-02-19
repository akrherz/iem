---
--- Store grid point geometries
---
CREATE TABLE grid(
  idx int UNIQUE
  );
 
 SELECT AddGeometryColumn('grid', 'geom', 4326, 'POINT', 2);
 CREATE index grid_idx on grid(idx);
 GRANT SELECT on grid to apache,nobody;
 
 ---
 --- Lookup table of observation events
 ---
 CREATE TABLE obtimes(
   valid timestamp with time zone UNIQUE
 );
 GRANT SELECT on obtimes to apache,nobody;
 
 ---
 --- Store the actual data, will have partitioned tables
 --- 
 CREATE TABLE data(
   grid_idx int REFERENCES grid(idx),
   valid timestamp with time zone,
   soil_moisture real,
   optical_depth real
 );
 GRANT SELECT on data to apache,nobody;
 
 CREATE TABLE data_2011_02() inherits (data);