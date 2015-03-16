--
-- Storage of average wind speed
ALTER TABLE summary
  ADD avg_sknt real;
ALTER TABLE summary
  ADD vector_avg_drct real;
