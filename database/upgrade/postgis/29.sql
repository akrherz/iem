CREATE TABLE ffg_2019(
  CONSTRAINT __ffg_2019_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2019_ugc_idx on ffg_2019(ugc);
CREATE INDEX ffg_2019_valid_idx on ffg_2019(valid);
GRANT ALL on ffg_2019 to ldm,mesonet;
GRANT SELECT on ffg_2019 to nobody,apache;

create table lsrs_2019( 
  CONSTRAINT __lsrs_2019_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz 
        and valid < '2020-01-01 00:00+00'::timestamptz)) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2019_valid_idx on lsrs_2019(valid);
CREATE INDEX lsrs_2019_wfo_idx on lsrs_2019(wfo);
GRANT SELECT on lsrs_2019 to nobody,apache;

CREATE TABLE raob_profile_2019() inherits (raob_profile);
GRANT SELECT on raob_profile_2019 to nobody,apache;
CREATE INDEX raob_profile_2019_fid_idx 
    on raob_profile_2019(fid);


CREATE TABLE warnings_2019() inherits (warnings);
CREATE INDEX warnings_2019_combo_idx on 
    warnings_2019(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2019_expire_idx on warnings_2019(expire);
CREATE INDEX warnings_2019_issue_idx on warnings_2019(issue);
CREATE INDEX warnings_2019_ugc_idx on warnings_2019(ugc);
CREATE INDEX warnings_2019_wfo_idx on warnings_2019(wfo);
CREATE INDEX warnings_2019_gid_idx on warnings_2019(gid);
-- Add some proper constraints to keep database cleaner
alter table warnings_2019 ADD CONSTRAINT warnings_2019_gid_fkey
        FOREIGN KEY(gid) REFERENCES ugcs(gid);
alter table warnings_2019 ALTER WFO SET NOT NULL;
alter table warnings_2019 ALTER eventid SET NOT NULL;
alter table warnings_2019 ALTER status SET NOT NULL;
alter table warnings_2019 ALTER ugc SET NOT NULL;
alter table warnings_2019 ALTER phenomena SET NOT NULL;
alter table warnings_2019 ALTER significance SET NOT NULL;
grant select on warnings_2019 to nobody,apache;
GRANT ALL on warnings_2019 to mesonet,ldm;


CREATE table sbw_2019() inherits (sbw);
create index sbw_2019_idx on sbw_2019(wfo,eventid,significance,phenomena);
create index sbw_2019_expire_idx on sbw_2019(expire);
create index sbw_2019_issue_idx on sbw_2019(issue);
create index sbw_2019_wfo_idx on sbw_2019(wfo);
CREATE INDEX sbw_2019_gix ON sbw_2019 USING GIST (geom);
grant select on sbw_2019 to apache,nobody;
