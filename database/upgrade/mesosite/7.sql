-- Storage of simple extent of stations
SELECT AddGeometryColumn('networks', 'extent', 4326, 'POLYGON', 2);