--- Soil Moisture Stations
CREATE TABLE sm_minute (
  station char(5),
  valid timestamp with time zone,

  -- Air Temperature
  TAir_C_Avg real,
  TAir_C_Avg_qc real,
  TAir_C_Avg_f char(1),

  -- Relative Humidity
  rh_avg real,
  rh_avg_qc real,
  rh_avg_f char(1),

  -- Solar Rad total kJ over 1 minute
  SlrkJ_Tot real,
  SlrkJ_Tot_qc real,
  SlrkJ_Tot_f char(1),

  -- Precip total
  Rain_in_Tot real,
  Rain_in_Tot_qc real,
  Rain_in_Tot_f char(1),

  -- 4 inch soil
  TSoil_C_Avg real,
  TSoil_C_Avg_qc real,
  TSoil_C_Avg_f char(1),

  -- wind speed mph
  WS_mph_S_WVT real,
  WS_mph_S_WVT_qc real,
  WS_mph_S_WVT_f char(1),

  -- wind speed max
  WS_mph_max real,
  WS_mph_max_qc real,
  WS_mph_max_f char(1),

  -- wind direction
  WindDir_D1_WVT real,
  WindDir_D1_WVT_qc real,
  WindDir_D1_WVT_f char(1),

  -- 12 inch VWC
  calcVWC12_Avg real,
  calcVWC12_Avg_qc real,
  calcVWC12_Avg_f char(1),

  -- 24 inch VWC
  calcVWC24_Avg real,
  calcVWC24_Avg_qc real,
  calcVWC24_Avg_f char(1),

  -- 50 inch VWC
  calcVWC50_Avg real,
  calcVWC50_Avg_qc real,
  calcVWC50_Avg_f char(1),

  -- 12 inch temp
  T12_C_Avg real,
  T12_C_Avg_qc real,
  T12_C_Avg_f char(1),

  -- 24 inch temp
  T24_C_Avg real,
  T24_C_Avg_qc real,
  T24_C_Avg_f char(1),

  -- 50 inch temp
  T50_C_Avg real,
  T50_C_Avg_qc real,
  T50_C_Avg_f char(1),

  bp_mb real,
  bp_mb_qc real,
  bp_mb_f char(1)
);
GRANT SELECT on sm_minute to nobody;
GRANT ALL on sm_minute to ldm,mesonet;

create table sm_minute_2019( 
  CONSTRAINT __t2019_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00')) 
  INHERITS (sm_minute);
CREATE UNIQUE INDEX sm_minute_2019_idx on sm_minute_2019(station, valid);
GRANT SELECT on sm_minute_2019 to nobody;
GRANT ALL on sm_minute_2019 to ldm,mesonet;

alter table sm_hourly add tair_c_max real;
alter table sm_hourly add tair_c_max_qc real;
alter table sm_hourly add tair_c_max_f char(1);

alter table sm_hourly add tair_c_min real;
alter table sm_hourly add tair_c_min_qc real;
alter table sm_hourly add tair_c_min_f char(1);