
create table lsrs_2017( 
  CONSTRAINT __lsrs_2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00'::timestamptz)) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2017_valid_idx on lsrs_2017(valid);
CREATE INDEX lsrs_2017_wfo_idx on lsrs_2017(wfo);
GRANT SELECT on lsrs_2017 to nobody,apache;

CREATE TABLE raob_profile_2017() inherits (raob_profile);
GRANT SELECT on raob_profile_2017 to nobody,apache;
CREATE INDEX raob_profile_2017_fid_idx 
	on raob_profile_2017(fid);


CREATE TABLE warnings_2017() inherits (warnings);
CREATE INDEX warnings_2017_combo_idx on 
	warnings_2017(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2017_expire_idx on warnings_2017(expire);
CREATE INDEX warnings_2017_issue_idx on warnings_2017(issue);
CREATE INDEX warnings_2017_ugc_idx on warnings_2017(ugc);
CREATE INDEX warnings_2017_wfo_idx on warnings_2017(wfo);
CREATE INDEX warnings_2017_gid_idx on warnings_2017(gid);
-- Add some proper constraints to keep database cleaner
alter table warnings_2017 ADD CONSTRAINT warnings_2017_gid_fkey
        FOREIGN KEY(gid) REFERENCES ugcs(gid);
alter table warnings_2017 ALTER issue SET NOT NULL;
alter table warnings_2017 ALTER expire SET NOT NULL;
alter table warnings_2017 ALTER updated SET NOT NULL;
alter table warnings_2017 ALTER WFO SET NOT NULL;
alter table warnings_2017 ALTER eventid SET NOT NULL;
alter table warnings_2017 ALTER status SET NOT NULL;
alter table warnings_2017 ALTER ugc SET NOT NULL;
alter table warnings_2017 ALTER phenomena SET NOT NULL;
alter table warnings_2017 ALTER significance SET NOT NULL;
alter table warnings_2017 ALTER init_expire SET NOT NULL;
alter table warnings_2017 ALTER product_issue SET NOT NULL;
grant select on warnings_2017 to nobody,apache;


CREATE table sbw_2017() inherits (sbw);
create index sbw_2017_idx on sbw_2017(wfo,eventid,significance,phenomena);
create index sbw_2017_expire_idx on sbw_2017(expire);
create index sbw_2017_issue_idx on sbw_2017(issue);
create index sbw_2017_wfo_idx on sbw_2017(wfo);
CREATE INDEX sbw_2017_gix ON sbw_2017 USING GIST (geom);
grant select on sbw_2017 to apache,nobody;
