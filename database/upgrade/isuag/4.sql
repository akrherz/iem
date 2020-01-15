--storage of second precip bucket
ALTER TABLE sm_hourly add rain_mm_2_tot real;
ALTER TABLE sm_hourly add rain_mm_2_tot_qc real;
ALTER TABLE sm_hourly add rain_mm_2_tot_f char(1);

ALTER TABLE sm_daily add rain_mm_2_tot real;
ALTER TABLE sm_daily add rain_mm_2_tot_qc real;
ALTER TABLE sm_daily add rain_mm_2_tot_f char(1);
