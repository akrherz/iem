-- Storage of Wind data
ALTER TABLE cli_data add resultant_wind_speed real;
ALTER TABLE cli_data add resultant_wind_direction real;
ALTER TABLE cli_data add highest_wind_speed real;
ALTER TABLE cli_data add highest_wind_direction real;
ALTER TABLE cli_data add highest_gust_speed real;
ALTER TABLE cli_data add highest_gust_direction real;
ALTER TABLE cli_data add average_wind_speed real;
