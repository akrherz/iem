

create table lsrs_2016( 
  CONSTRAINT __lsrs_2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2016_valid_idx on lsrs_2016(valid);
CREATE INDEX lsrs_2016_wfo_idx on lsrs_2016(wfo);
GRANT SELECT on lsrs_2016 to nobody,apache;

CREATE TABLE raob_profile_2016() inherits (raob_profile);
GRANT SELECT on raob_profile_2016 to nobody,apache;
CREATE INDEX raob_profile_2016_fid_idx 
	on raob_profile_2016(fid);

-- !!!!!!!!!!!!! WARNING !!!!!!!!!!!!
-- look what was done in 9.sql and replicate that for 2017 updates
-- look at 15.sql too :(
CREATE TABLE warnings_2016() inherits (warnings);
CREATE INDEX warnings_2016_combo_idx on 
	warnings_2016(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2016_expire_idx on warnings_2016(expire);
CREATE INDEX warnings_2016_issue_idx on warnings_2016(issue);
CREATE INDEX warnings_2016_ugc_idx on warnings_2016(ugc);
CREATE INDEX warnings_2016_wfo_idx on warnings_2016(wfo);
-- Add some proper constraints to keep database cleaner
alter table warnings_2016 ADD CONSTRAINT warnings_2016_gid_fkey
        FOREIGN KEY(gid) REFERENCES ugcs(gid);
alter table warnings_2016 ALTER issue SET NOT NULL;
alter table warnings_2016 ALTER expire SET NOT NULL;
alter table warnings_2016 ALTER updated SET NOT NULL;
alter table warnings_2016 ALTER WFO SET NOT NULL;
alter table warnings_2016 ALTER eventid SET NOT NULL;
alter table warnings_2016 ALTER status SET NOT NULL;
alter table warnings_2016 ALTER ugc SET NOT NULL;
alter table warnings_2016 ALTER phenomena SET NOT NULL;
alter table warnings_2016 ALTER significance SET NOT NULL;
alter table warnings_2016 ALTER init_expire SET NOT NULL;
alter table warnings_2016 ALTER product_issue SET NOT NULL;
grant select on warnings_2016 to nobody,apache;

CREATE table sbw_2016() inherits (sbw);
create index sbw_2016_idx on sbw_2016(wfo,eventid,significance,phenomena);
create index sbw_2016_expire_idx on sbw_2016(expire);
create index sbw_2016_issue_idx on sbw_2016(issue);
create index sbw_2016_wfo_idx on sbw_2016(wfo);
CREATE INDEX sbw_2016_gix ON sbw_2016 USING GIST (geom);
grant select on sbw_2016 to apache,nobody;
