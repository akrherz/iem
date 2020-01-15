
ALTER TABLE sm_hourly add etapples real;
ALTER TABLE sm_hourly add etapples_qc real;
ALTER TABLE sm_hourly add etapples_f char(1);

ALTER TABLE sm_daily add etapples real;
ALTER TABLE sm_daily add etapples_qc real;
ALTER TABLE sm_daily add etapples_f char(1);

ALTER TABLE sm_daily add solarradcalc real;
ALTER TABLE sm_daily add solarradcalc_qc real;
ALTER TABLE sm_daily add solarradcalc_f char(1);

ALTER TABLE sm_daily add rh_avg real;
ALTER TABLE sm_daily add rh_avg_qc real;
ALTER TABLE sm_daily add rh_avg_f char(1);

ALTER TABLE sm_daily add ws_mph real;
ALTER TABLE sm_daily add ws_mph_qc real;
ALTER TABLE sm_daily add ws_mph_f char(1);

ALTER TABLE sm_daily add ws_mph_max real;
ALTER TABLE sm_daily add ws_mph_max_qc real;
ALTER TABLE sm_daily add ws_mph_max_f char(1);

ALTER TABLE sm_daily add ws_mph_tmx timestamptz;
ALTER TABLE sm_daily add ws_mph_tmx_qc timestamptz;
ALTER TABLE sm_daily add ws_mph_tmx_f char(1);