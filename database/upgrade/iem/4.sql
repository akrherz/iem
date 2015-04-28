--
-- Storage of Daily average RH and max/min RH
ALTER TABLE summary
  ADD avg_rh real;

ALTER TABLE summary
  ADD min_rh real;

ALTER TABLE summary
  ADD max_rh real;
