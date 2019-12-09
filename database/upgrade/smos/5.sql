ALTER TABLE data rename to data_old;

 --- 
 CREATE TABLE data(
   grid_idx int REFERENCES grid(idx),
   valid timestamp with time zone,
   soil_moisture real,
   optical_depth real
 ) PARTITION by range(valid);
 ALTER TABLE data OWNER to mesonet;
 GRANT ALL on data to ldm;
 GRANT SELECT on data to apache,nobody;
 

do
$do$
declare
     year int;
     month int;
     mytable varchar;
begin
    for year in 2010..2019
    loop
        for month in 1..12
        loop
            mytable := format($f$data_%s_%s$f$,
                year, lpad(month::text, 2, '0'));
            execute format($f$
                ALTER TABLE %s NO INHERIT data_old
                $f$, mytable);
            execute format($f$
                ALTER TABLE data ATTACH PARTITION %s
                FOR VALUES FROM ('%s-%s-01 00:00+00') to ('%s-%s-01 00:00+00')
            $f$, mytable, year, month,
                case when month = 12 then year + 1 else year end,
                case when month = 12 then 1 else month + 1 end);

        end loop;
    end loop;
end;
$do$;

 do
$do$
declare
     year int;
     month int;
     mytable varchar;
begin
    for year in 2020..2030
    loop
        for month in 1..12
        loop
            mytable := format($f$data_%s_%s$f$,
                year, lpad(month::text, 2, '0'));
            execute format($f$
                create table %s partition of data
                for values from ('%s-%s-01 00:00+00') to ('%s-%s-01 00:00+00')
                $f$, mytable,
                year, month,
                case when month = 12 then year + 1 else year end,
                case when month = 12 then 1 else month + 1 end);
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
                CREATE INDEX %s_grid_idx on %s(grid_idx)
            $f$, mytable, mytable);
            execute format($f$
                CREATE INDEX %s_valid_idx on %s(valid)
            $f$, mytable, mytable);
        end loop;
    end loop;
end;
$do$;

DROP TABLE data_old;
