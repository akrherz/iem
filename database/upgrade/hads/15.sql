-- HML forecast data is kind of a one-off with no inheritence
do
$do$
declare
     year int;
     mytable varchar;
begin
    for year in 2021..2030
    loop
        mytable := format($f$hml_forecast_data_%s$f$, year);
        execute format($f$
            CREATE TABLE %s(
            hml_forecast_id int REFERENCES hml_forecast(id),
            valid timestamptz,
            primary_value real,
            secondary_value real)
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
        execute format($f$
            CREATE INDEX on %s(hml_forecast_id)
        $f$, mytable);
    end loop;
end;
$do$;