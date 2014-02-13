--- ========================================================================
--- Storage of Soil Nitrate Data
---
CREATE TABLE soil_nitrate_data(
  site varchar(24),
  plotid varchar(24),
  depth varchar(24),
  varname varchar(24),
  year smallint,
  value varchar(32),
  updated timestamptz default now()
);

CREATE TABLE soil_nitrate_data_log(
  site varchar(24),
  plotid varchar(24),
  depth varchar(24),
  varname varchar(24),
  year smallint,
  value varchar(32),
  updated timestamptz default now()
);

CREATE OR REPLACE FUNCTION soil_nitrate_insert_before_F()
RETURNS TRIGGER
 AS $BODY$
DECLARE
    result INTEGER; 
BEGIN
    result = (select count(*) from soil_nitrate_data
                where site = new.site and plotid = new.plotid and
                varname = new.varname and year = new.year and
                depth = new.depth and
                (value = new.value or (value is null and new.value is null))
               );

	-- Data is duplication, no-op
    IF result = 1 THEN
        RETURN null;
    END IF;

    result = (select count(*) from soil_nitrate_data
                where site = new.site and plotid = new.plotid and
                varname = new.varname and year = new.year
                and depth = new.depth);

	-- Data is a new value!
    IF result = 1 THEN
    	UPDATE soil_nitrate_data SET value = new.value, updated = now()
    	WHERE site = new.site and plotid = new.plotid and
                varname = new.varname and year = new.year and
                depth = new.depth;
        INSERT into soil_nitrate_data_log SELECT * from soil_nitrate_data WHERE
        		site = new.site and plotid = new.plotid and
                varname = new.varname and year = new.year and depth = new.depth;
        RETURN null;
    END IF;

    INSERT into soil_nitrate_data_log (site, plotid, varname, year, depth, value)
    VALUES (new.site, new.plotid, new.varname, new.year, new.depth, new.value);

    -- The default branch is to return "NEW" which
    -- causes the original INSERT to go forward
    RETURN new;

END; $BODY$
LANGUAGE 'plpgsql' SECURITY DEFINER;

CREATE TRIGGER soil_nitrate_insert_before_T
   before insert
   ON soil_nitrate_data
   FOR EACH ROW
   EXECUTE PROCEDURE soil_nitrate_insert_before_F();
  
CREATE UNIQUE index soil_nitrate_data_idx on 
	soil_nitrate_data(site, plotid, varname, year, depth);
GRANT SELECT on soil_nitrate_data to nobody,apache;



--- ==========================================================================
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
                (value = new.value or (value is null and new.value is null))
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
GRANT SELECT on agronomic_data to nobody,apache;