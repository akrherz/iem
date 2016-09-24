DO $$
DECLARE
  rec record;
BEGIN
FOR rec in SELECT generate_series(1928, 1940) as year LOOP
EXECUTE format('create table summary_'|| rec.year || '(
  CONSTRAINT __summary_'|| rec.year || '_check
  CHECK(day >= %L::date
        and day <= %L::date))
  INHERITS (summary)', rec.year || '-01-01', rec.year || '-12-31');
EXECUTE 'CREATE INDEX summary_'|| rec.year || '_day_idx on summary_'|| rec.year || '(day)';
EXECUTE 'CREATE UNIQUE INDEX summary_'|| rec.year || '_iemid_day_idx on summary_'|| rec.year || '(iemid, day)';
EXECUTE 'GRANT SELECT on summary_'|| rec.year || ' to nobody,apache';
EXECUTE 'alter table summary_'|| rec.year || '
  add foreign key(iemid)
  references stations(iemid) ON DELETE CASCADE';
END LOOP;
END$$;
  