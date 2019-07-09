-- Storage of daily min and max RH, needed for downstream apps
ALTER TABLE iemre_daily add min_rh real;
ALTER TABLE iemre_daily add max_rh real;
