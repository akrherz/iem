-- Helper to upscale data
ALTER TABLE sm_hourly add obs_count int;
ALTER TABLE sm_daily add obs_count int;

ALTER TABLE sm_minute add rain_in_2_tot real;
ALTER TABLE sm_minute add rain_in_2_tot_qc real;
ALTER TABLE sm_minute add rain_in_2_tot_f char(1);

ALTER TABLE sm_minute add calcVWC02_Avg real;
ALTER TABLE sm_minute add calcVWC02_Avg_qc real;
ALTER TABLE sm_minute add calcVWC02_Avg_f char(1);

ALTER TABLE sm_minute add calcVWC04_Avg real;
ALTER TABLE sm_minute add calcVWC04_Avg_qc real;
ALTER TABLE sm_minute add calcVWC04_Avg_f char(1);

ALTER TABLE sm_minute add calcVWC06_Avg real;
ALTER TABLE sm_minute add calcVWC06_Avg_qc real;
ALTER TABLE sm_minute add calcVWC06_Avg_f char(1);

ALTER TABLE sm_minute add calcVWC08_Avg real;
ALTER TABLE sm_minute add calcVWC08_Avg_qc real;
ALTER TABLE sm_minute add calcVWC08_Avg_f char(1);

ALTER TABLE sm_minute add calcVWC12_Avg real;
ALTER TABLE sm_minute add calcVWC12_Avg_qc real;
ALTER TABLE sm_minute add calcVWC12_Avg_f char(1);

ALTER TABLE sm_minute add calcVWC16_Avg real;
ALTER TABLE sm_minute add calcVWC16_Avg_qc real;
ALTER TABLE sm_minute add calcVWC16_Avg_f char(1);

ALTER TABLE sm_minute add calcVWC20_Avg real;
ALTER TABLE sm_minute add calcVWC20_Avg_qc real;
ALTER TABLE sm_minute add calcVWC20_Avg_f char(1);

ALTER TABLE sm_minute add T02_C_Avg real;
ALTER TABLE sm_minute add T02_C_Avg_qc real;
ALTER TABLE sm_minute add T02_C_Avg_f char(1);

ALTER TABLE sm_minute add T04_C_Avg real;
ALTER TABLE sm_minute add T04_C_Avg_qc real;
ALTER TABLE sm_minute add T04_C_Avg_f char(1);

ALTER TABLE sm_minute add T06_C_Avg real;
ALTER TABLE sm_minute add T06_C_Avg_qc real;
ALTER TABLE sm_minute add T06_C_Avg_f char(1);

ALTER TABLE sm_minute add T08_C_Avg real;
ALTER TABLE sm_minute add T08_C_Avg_qc real;
ALTER TABLE sm_minute add T08_C_Avg_f char(1);

ALTER TABLE sm_minute add T16_C_Avg real;
ALTER TABLE sm_minute add T16_C_Avg_qc real;
ALTER TABLE sm_minute add T16_C_Avg_f char(1);

ALTER TABLE sm_minute add T20_C_Avg real;
ALTER TABLE sm_minute add T20_C_Avg_qc real;
ALTER TABLE sm_minute add T20_C_Avg_f char(1);

ALTER TABLE sm_minute add lwmv_1 real;
ALTER TABLE sm_minute add lwmv_1_qc real;
ALTER TABLE sm_minute add lwmv_1_f character(1);
ALTER TABLE sm_minute add lwmv_2 real;
ALTER TABLE sm_minute add lwmv_2_qc real;
ALTER TABLE sm_minute add lwmv_2_f character(1);
ALTER TABLE sm_minute add lwmdry_1_tot real;
ALTER TABLE sm_minute add lwmdry_1_tot_qc real;
ALTER TABLE sm_minute add lwmdry_1_tot_f character(1);
ALTER TABLE sm_minute add lwmcon_1_tot real;
ALTER TABLE sm_minute add lwmcon_1_tot_qc real;
ALTER TABLE sm_minute add lwmcon_1_tot_f character(1);
ALTER TABLE sm_minute add lwmwet_1_tot real;
ALTER TABLE sm_minute add lwmwet_1_tot_qc real;
ALTER TABLE sm_minute add lwmwet_1_tot_f character(1);
ALTER TABLE sm_minute add lwmdry_2_tot real;
ALTER TABLE sm_minute add lwmdry_2_tot_qc real;
ALTER TABLE sm_minute add lwmdry_2_tot_f character(1);
ALTER TABLE sm_minute add lwmcon_2_tot real;
ALTER TABLE sm_minute add lwmcon_2_tot_qc real;
ALTER TABLE sm_minute add lwmcon_2_tot_f character(1);
ALTER TABLE sm_minute add lwmwet_2_tot real;
ALTER TABLE sm_minute add lwmwet_2_tot_qc real;
ALTER TABLE sm_minute add lwmwet_2_tot_f character(1);

ALTER TABLE sm_minute add lwmdry_lowbare_tot real;
ALTER TABLE sm_minute add lwmdry_lowbare_tot_qc real;
ALTER TABLE sm_minute add lwmdry_lowbare_tot_f char(1);
ALTER TABLE sm_minute add lwmcon_lowbare_tot real;
ALTER TABLE sm_minute add lwmcon_lowbare_tot_qc real;
ALTER TABLE sm_minute add lwmcon_lowbare_tot_f char(1);
ALTER TABLE sm_minute add lwmwet_lowbare_tot real;
ALTER TABLE sm_minute add lwmwet_lowbare_tot_qc real;
ALTER TABLE sm_minute add lwmwet_lowbare_tot_f char(1);
ALTER TABLE sm_minute add lwmdry_highbare_tot real;
ALTER TABLE sm_minute add lwmdry_highbare_tot_qc real;
ALTER TABLE sm_minute add lwmdry_highbare_tot_f char(1);
ALTER TABLE sm_minute add lwmcon_highbare_tot real;
ALTER TABLE sm_minute add lwmcon_highbare_tot_qc real;
ALTER TABLE sm_minute add lwmcon_highbare_tot_f char(1);
ALTER TABLE sm_minute add lwmwet_highbare_tot real;
ALTER TABLE sm_minute add lwmwet_highbare_tot_qc real;
ALTER TABLE sm_minute add lwmwet_highbare_tot_f char(1);
