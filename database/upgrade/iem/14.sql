-- Storage of max/min feels like
ALTER TABLE summary ADD max_feel real;
ALTER TABLE summary ADD min_feel real;
ALTER TABLE summary ADD avg_feel real;

ALTER TABLE current add feel real;
ALTER TABLE current_log add feel real;
ALTER TABLE current_tmp add feel real;
