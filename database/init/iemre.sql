-- We want Postgis
CREATE EXTENSION postgis;

-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz
);
INSERT into iem_schema_manager_version values (0, now());

-- Our baseline grid
CREATE TABLE iemre_grid(
    gid int NOT NULL, -- (gridx + gridy * 488) - 1
    cell_center geometry(Point, 4326),
    cell_polygon geometry(Polygon, 4326),
    hasdata boolean,
    gridx int,
    gridy int
);
GRANT ALL on iemre_grid to mesonet,ldm;
GRANT SELECT on iemre_grid to nobody,apache;

-- fill out the grid, since we can
do
$do$
declare
     x int;
     y int;
begin
    for x in 0..487
    loop
        for y in 0..215
        loop
        execute format($f$
            INSERT into iemre_grid(gid, cell_center, hasdata, gridx, gridy,
            cell_polygon)
            VALUES (%s, 'SRID=4326;POINT(%s %s)', 't', %s, %s,
            'SRID=4326;Polygon((%s %s, %s %s, %s %s, %s %s, %s %s))')
        $f$, x + y * 488, -125.9375 + x * 0.125, 23.0625 + y * 0.125, x, y,
        -125.9375 + x * 0.125 - 0.0625, 23.0625 + y * 0.125 - 0.0625,
        -125.9375 + x * 0.125 - 0.0625, 23.0625 + y * 0.125 + 0.0625,
        -125.9375 + x * 0.125 + 0.0625, 23.0625 + y * 0.125 + 0.0625,
        -125.9375 + x * 0.125 + 0.0625, 23.0625 + y * 0.125 - 0.0625,
        -125.9375 + x * 0.125 - 0.0625, 23.0625 + y * 0.125 - 0.0625
        );
        end loop;
    end loop;
end;
$do$;


-- Create indices
CREATE INDEX iemre_grid_gix ON iemre_grid USING GIST (cell_center);
CREATE INDEX iemre_grid_cell_gix ON iemre_grid USING GIST (cell_polygon);
CREATE UNIQUE INDEX iemre_grid_gid_idx on iemre_grid(gid);
CREATE UNIQUE INDEX iemre_grid_idx on iemre_grid(gridx, gridy);

-- _______________________________________________________________________
-- Storage of daily analysis
CREATE TABLE iemre_daily(
    gid int REFERENCES iemre_grid(gid),
    valid date,
    high_tmpk real,
    low_tmpk real,
    high_tmpk_12z real,
    low_tmpk_12z real,
    p01d real,
    p01d_12z real,
    rsds real,
    snow_12z real,
    snowd_12z real,
    avg_dwpk real,
    wind_speed real,
    power_swdn real,
    min_rh real,
    max_rh real
) PARTITION by RANGE (valid);
GRANT ALL on iemre_daily to mesonet,ldm;
GRANT SELECT on iemre_daily to nobody,apache;

CREATE INDEX on iemre_daily(valid);
CREATE UNIQUE INDEX on iemre_daily(gid, valid);


do
$do$
declare
     year int;
begin
    for year in 1893..2030
    loop
        execute format($f$
            create table iemre_daily_%s partition of iemre_daily
            for values from ('%s-01-01') to ('%s-01-01')
        $f$, year, year, year + 1);
        execute format($f$
            GRANT ALL on iemre_daily_%s to mesonet,ldm
        $f$, year);
        execute format($f$
            GRANT SELECT on iemre_daily_%s to nobody,apache
        $f$, year);
    end loop;
end;
$do$;

-- _______________________________________________________________________
-- Storage of daily climatology
CREATE TABLE iemre_dailyc(
    gid int REFERENCES iemre_grid(gid),
    valid date,
    high_tmpk real,
    low_tmpk real,
    p01d real
);
GRANT ALL on iemre_dailyc to mesonet,ldm;
GRANT SELECT on iemre_dailyc to nobody,apache;

CREATE INDEX on iemre_dailyc(valid);
CREATE UNIQUE INDEX on iemre_dailyc(gid, valid);

-- _______________________________________________________________________
-- Storage of hourly analysis
-- NOTE: we had troubles getting cute with variable types, just use real
CREATE TABLE iemre_hourly(
    gid int REFERENCES iemre_grid(gid),
    valid timestamptz,
    skyc real,
    tmpk real,
    dwpk real,
    uwnd real,
    vwnd real,
    p01m real
) PARTITION by RANGE (valid);
GRANT ALL on iemre_hourly to mesonet,ldm;
GRANT SELECT on iemre_hourly to nobody,apache;

CREATE INDEX on iemre_hourly(valid);
CREATE UNIQUE INDEX on iemre_hourly(gid, valid);


do
$do$
declare
     year int;
begin
    for year in 1980..2030
    loop
        for month in 1..12
        loop
            execute format($f$
                create table iemre_hourly_%s%s partition of iemre_hourly
                for values from ('%s-%s-01 00:00+00') to ('%s-%s-01 00:00+00')
            $f$, year, lpad(month::text, 2, '0'), year, month,
            case when month = 12 then year + 1 else year end,
            case when month = 12 then 1 else month + 1 end);
            execute format($f$
                GRANT ALL on iemre_hourly_%s%s to mesonet,ldm
            $f$, year, lpad(month::text, 2, '0'));
            execute format($f$
                GRANT SELECT on iemre_hourly_%s%s to nobody,apache
            $f$, year, lpad(month::text, 2, '0'));
        end loop;
    end loop;
end;
$do$;
