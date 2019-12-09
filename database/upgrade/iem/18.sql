--- ugly dance here
ALTER TABLE summary RENAME to summary_old;

-- main storage of summary data
CREATE TABLE summary (
	iemid int REFERENCES stations(iemid),
    max_tmpf real,
    min_tmpf real,
    day date,
    max_sknt real,
    max_gust real,
    max_sknt_ts timestamp with time zone,
    max_gust_ts timestamp with time zone,
    max_dwpf real,
    min_dwpf real,
    pday real,
    pmonth real,
    snow real,
    snowd real,
    max_tmpf_qc character(1),
    min_tmpf_qc character(1),
    pday_qc character(1),
    snow_qc character(1),
    snoww real,
    max_drct real,
    max_srad smallint,
    coop_tmpf real,
    coop_valid timestamp with time zone,
    et_inch real,
    srad_mj real,
    avg_sknt real,
    vector_avg_drct real,
    avg_rh real,
    min_rh real,
    max_rh real,
    max_water_tmpf real,
    min_water_tmpf real,
    max_feel real,
    avg_feel real,
    min_feel real
) PARTITION by range(day);
ALTER TABLE summary OWNER to mesonet;
GRANT ALL on summary to ldm;
GRANT SELECT on summary to nobody,apache;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 1928..2019
    loop
        mytable := format($f$summary_%s$f$, year);
        execute format($f$
            ALTER TABLE %s NO INHERIT summary_old
            $f$, mytable);
        execute format($f$
            ALTER TABLE summary ATTACH PARTITION %s
            FOR VALUES FROM ('%s-01-01') to ('%s-01-01')
        $f$, mytable, year, year + 1);
    end loop;
end;
$do$;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2020..2030
    loop
        mytable := format($f$summary_%s$f$, year);
        execute format($f$
            create table %s partition of summary
            for values from ('%s-01-01') to ('%s-01-01')
            $f$, mytable, year, year + 1);
        execute format($f$
            ALTER TABLE %s ADD foreign key(iemid)
            references stations(iemid) ON DELETE CASCADE;
        $f$, mytable);
        execute format($f$
            ALTER TABLE %s OWNER to mesonet
        $f$, mytable);
        execute format($f$
            GRANT ALL on %s to ldm
        $f$, mytable);
        execute format($f$
            GRANT SELECT on %s to nobody,apache
        $f$, mytable);
        -- Indices
        execute format($f$
            CREATE INDEX %s_idx on %s(iemid, day)
        $f$, mytable, mytable);
        execute format($f$
            CREATE INDEX %s_day_idx on %s(day)
        $f$, mytable, mytable);
    end loop;
end;
$do$;

DROP TABLE summary_old;
