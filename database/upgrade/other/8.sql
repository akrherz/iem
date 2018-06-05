-- More columns for new soil moisture sensor
ALTER TABLE flux_data add vwc real;
ALTER TABLE flux_data add ec real;
ALTER TABLE flux_data add t real;
ALTER TABLE flux_data add p real;
ALTER TABLE flux_data add pa real;
ALTER TABLE flux_data add vr real;
