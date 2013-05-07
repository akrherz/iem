CREATE TABLE agronomic_data(
  site varchar(24),
  plotid varchar(24),
  varname varchar(24),
  year smallint,
  value real);
CREATE UNIQUE index agronomic_data_idx on agronomic_data(site, plotid, varname,
  year);