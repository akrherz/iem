CREATE FUNCTION gdd48(real, real) RETURNS numeric
    LANGUAGE sql
    AS $_$select (( (CASE WHEN $1 > 48 THEN (case when $1 > 86 THEN 86 ELSE $1 END ) - 48 ELSE 0 END) + (CASE WHEN $2 > 48 THEN $2 - 48 ELSE 0 END) ) / 2.0)::numeric$_$;

--
-- base, max, high, low
 CREATE FUNCTION gddXX(real, real, real, real) RETURNS numeric
    LANGUAGE sql
    AS $_$select (( (CASE WHEN $3 > $1 THEN (case when $3 > $2 THEN $2 ELSE $3 END ) - $1 ELSE 0 END) + 
    (CASE WHEN $4 > $1 THEN $4 - $1 ELSE 0 END) ) / 2.0)::numeric$_$;
 