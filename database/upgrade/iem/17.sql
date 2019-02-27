ALTER TABLE current ADD peak_wind_gust real;
ALTER TABLE current ADD peak_wind_drct real;
ALTER TABLE current ADD peak_wind_time timestamptz;

ALTER TABLE current_log ADD peak_wind_gust real;
ALTER TABLE current_log ADD peak_wind_drct real;
ALTER TABLE current_log ADD peak_wind_time timestamptz;

ALTER TABLE current_tmp ADD peak_wind_gust real;
ALTER TABLE current_tmp ADD peak_wind_drct real;
ALTER TABLE current_tmp ADD peak_wind_time timestamptz;
