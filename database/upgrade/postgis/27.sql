CREATE TABLE ffg_2018(
  CONSTRAINT __ffg_2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2018_ugc_idx on ffg_2018(ugc);
CREATE INDEX ffg_2018_valid_idx on ffg_2018(valid);
GRANT ALL on ffg_2018 to ldm,mesonet;
GRANT SELECT on ffg_2018 to nobody,apache;

create table lsrs_2018( 
  CONSTRAINT __lsrs_2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00'::timestamptz)) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2018_valid_idx on lsrs_2018(valid);
CREATE INDEX lsrs_2018_wfo_idx on lsrs_2018(wfo);
GRANT SELECT on lsrs_2018 to nobody,apache;

CREATE TABLE raob_profile_2018() inherits (raob_profile);
GRANT SELECT on raob_profile_2018 to nobody,apache;
CREATE INDEX raob_profile_2018_fid_idx 
    on raob_profile_2018(fid);


CREATE TABLE warnings_2018() inherits (warnings);
CREATE INDEX warnings_2018_combo_idx on 
    warnings_2018(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2018_expire_idx on warnings_2018(expire);
CREATE INDEX warnings_2018_issue_idx on warnings_2018(issue);
CREATE INDEX warnings_2018_ugc_idx on warnings_2018(ugc);
CREATE INDEX warnings_2018_wfo_idx on warnings_2018(wfo);
CREATE INDEX warnings_2018_gid_idx on warnings_2018(gid);
-- Add some proper constraints to keep database cleaner
alter table warnings_2018 ADD CONSTRAINT warnings_2018_gid_fkey
        FOREIGN KEY(gid) REFERENCES ugcs(gid);
alter table warnings_2018 ALTER WFO SET NOT NULL;
alter table warnings_2018 ALTER eventid SET NOT NULL;
alter table warnings_2018 ALTER status SET NOT NULL;
alter table warnings_2018 ALTER ugc SET NOT NULL;
alter table warnings_2018 ALTER phenomena SET NOT NULL;
alter table warnings_2018 ALTER significance SET NOT NULL;
grant select on warnings_2018 to nobody,apache;
GRANT ALL on warnings_2018 to mesonet,ldm;


CREATE table sbw_2018() inherits (sbw);
create index sbw_2018_idx on sbw_2018(wfo,eventid,significance,phenomena);
create index sbw_2018_expire_idx on sbw_2018(expire);
create index sbw_2018_issue_idx on sbw_2018(issue);
create index sbw_2018_wfo_idx on sbw_2018(wfo);
CREATE INDEX sbw_2018_gix ON sbw_2018 USING GIST (geom);
grant select on sbw_2018 to apache,nobody;
