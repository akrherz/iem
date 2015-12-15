-- Update roads_base to track that validity of the segment in time
ALTER TABLE roads_base add archive_begin timestamptz;
ALTER TABLE roads_base add archive_end timestamptz;