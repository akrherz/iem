-- paritioning of sm_minute
ALTER TABLE sm_minute RENAME to sm_minute_old;

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
) PARTITION by range(valid);
ALTER TABLE sm_minute OWNER to mesonet;
GRANT SELECT on sm_minute to nobody;
GRANT ALL on sm_minute to ldm;
CREATE INDEX on sm_minute(station, valid);

-- Fix old tables
do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2019..2020
    loop
        mytable := format($f$sm_minute_%s$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT sm_minute_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE sm_minute ATTACH PARTITION %s
            FOR VALUES FROM ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
        $f$, mytable, year, year + 1);
    end loop;
end;
$do$;

-- Add new tables
do
$do$
declare
     year int;
begin
    for year in 2021..2030
    loop
        execute format($f$
            create table sm_minute_%s partition of sm_minute
            for values from ('%s-01-01 00:00+00') to ('%s-01-01 00:00+00')
        $f$, year, year, year + 1);
        execute format($f$
            GRANT ALL on sm_minute_%s to mesonet,ldm
        $f$, year);
        execute format($f$
            GRANT SELECT on sm_minute_%s to nobody,apache
        $f$, year);
    end loop;
end;
$do$;

DROP table sm_minute_old;
