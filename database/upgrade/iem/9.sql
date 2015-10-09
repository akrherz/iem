-- Storage of battery voltage
ALTER TABLE current ADD battery real;
ALTER TABLE current_log ADD battery real;

-- Storage of water temp
ALTER TABLE current ADD water_tmpf real;
ALTER TABLE current_log ADD water_tmpf real;
ALTER TABLE summary ADD max_water_tmpf real;
ALTER TABLE summary ADD min_water_tmpf real;