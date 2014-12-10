---
--- Remove the no-longer-used (I hope) gtype column!
---

ALTER TABLE warnings DROP COLUMN gtype;

--- DO $$
--- DECLARE
---    rec   record;
--- BEGIN
--- FOR rec IN SELECT generate_series(1986,2015) as year LOOP
---  EXECUTE 'ALTER TABLE warnings_'|| rec.year || ' DROP COLUMN gtype';
--- END LOOP;
--- END$$;