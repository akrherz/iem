-- Remove unused(?) column
ALTER TABLE roads_base DROP tempval;



-- drop legacy roads_base tables
DROP TABLE roads_base_2005;
DROP TABLE roads_base_2006;
DROP TABLE roads_base_2009;
DROP TABLE roads_base_2010;
DROP TABLE roads_base_2011;
DROP TABLE roads_base_2013;
