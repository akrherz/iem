-- Storage of CF6 data
CREATE TABLE cf6_data(
    station text,
    valid date,
    product text,
    high real,
    low real,
    avg_temp real,
    dep_temp real,
    hdd real,
    cdd real,
    precip real,
    snow real,
    snowd_12z real,
    avg_smph real,
    max_smph real,
    avg_drct real,
    minutes_sunshine real,
    possible_sunshine real,
    cloud_ss real,
    wxcodes text,
    gust_smph real,
    gust_drct real
) PARTITION by range(valid);
CREATE UNIQUE INDEX on cf6_data(station, valid);
ALTER TABLE cf6_data OWNER to mesonet;
GRANT ALL on cf6_data to ldm;
GRANT SELECT on cf6_data to nobody;

do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2000..2030
    loop
        mytable := format($f$cf6_data_%s$f$, year);
        execute format($f$
            create table %s partition of cf6_data
            for values from ('%s-01-01') to ('%s-01-01')
            $f$, mytable, year, year + 1);
        execute format($f$
            ALTER TABLE %s OWNER to mesonet
        $f$, mytable);
        execute format($f$
            GRANT ALL on %s to ldm
        $f$, mytable);
        execute format($f$
            GRANT SELECT on %s to nobody,apache
        $f$, mytable);
    end loop;
end;
$do$;
