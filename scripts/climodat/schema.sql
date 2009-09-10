
DROP table r_precipevents;
CREATE table r_precipevents(
  stationid char(6),
  climoweek smallint,
  maxval real,
  meanval real,
  cat1e smallint,
  cat2e smallint,
  cat3e smallint,
  cat4e smallint,
  cat5e smallint,
  missing smallint 
);
grant select on r_precipevents to nobody;
create unique index r_precipevents_idx 
 on r_precipevents(stationid, climoweek);

DROP table r_monthly;
CREATE table r_monthly(
  stationid char(6),
  monthdate date,
  gdd40 smallint,
  gdd48 smallint,
  gdd50 smallint,
  gdd52 smallint
);
grant select on r_rmonthly to nobody;
create unique index r_monthly_idx
 on r_monthly(stationid, monthdate);
