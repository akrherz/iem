---
--- Storage of Agronomic Data
---
CREATE TABLE agronomic_data(
  site varchar(24),
  plotid varchar(24),
  varname varchar(24),
  year smallint,
  value varchar(32),
  updated timestamptz default now()
);

CREATE TABLE agronomic_data_log(
  site varchar(24),
  plotid varchar(24),
  varname varchar(24),
  year smallint,
  value varchar(32),
  updated timestamptz default now()
);

CREATE OR REPLACE FUNCTION agronomic_insert_before_F()
RETURNS TRIGGER
 AS $BODY$
DECLARE
    result INTEGER; 
BEGIN
    result = (select count(*) from agronomic_data
                where site = new.site and plotid = new.plotid and
                varname = new.varname and year = new.year and
                value = new.value
               );

	-- Data is duplication, no-op
    IF result = 1 THEN
        RETURN null;
    END IF;

    result = (select count(*) from agronomic_data
                where site = new.site and plotid = new.plotid and
                varname = new.varname and year = new.year);

	-- Data is a new value!
    IF result = 1 THEN
    	UPDATE agronomic_data SET value = new.value, updated = now()
    	WHERE site = new.site and plotid = new.plotid and
                varname = new.varname and year = new.year;
        INSERT into agronomic_data_log SELECT * from agronomic_data WHERE
        		site = new.site and plotid = new.plotid and
                varname = new.varname and year = new.year;
        RETURN null;
    END IF;

    INSERT into agronomic_data_log (site, plotid, varname, year, value)
    VALUES (new.site, new.plotid, new.varname, new.year, new.value);

    -- The default branch is to return "NEW" which
    -- causes the original INSERT to go forward
    RETURN new;

END; $BODY$
LANGUAGE 'plpgsql' SECURITY DEFINER;

CREATE TRIGGER agronomic_insert_before_T
   before insert
   ON agronomic_data
   FOR EACH ROW
   EXECUTE PROCEDURE agronomic_insert_before_F();
  
CREATE UNIQUE index agronomic_data_idx on 
	agronomic_data(site, plotid, varname, year);