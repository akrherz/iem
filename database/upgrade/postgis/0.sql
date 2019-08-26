

create table lsrs_2015( 
  CONSTRAINT __lsrs_2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (lsrs);
CREATE INDEX lsrs_2015_valid_idx on lsrs_2015(valid);
CREATE INDEX lsrs_2015_wfo_idx on lsrs_2015(wfo);
GRANT SELECT on lsrs_2015 to nobody,apache;

CREATE TABLE raob_profile_2015() inherits (raob_profile);
GRANT SELECT on raob_profile_2015 to nobody,apache;
CREATE INDEX raob_profile_2015_fid_idx 
	on raob_profile_2015(fid);

-- !!!!!!!!!!!!! WARNING !!!!!!!!!!!!
-- look what was done in 9.sql and replicate that for 2016 updates
CREATE TABLE warnings_2015() inherits (warnings);
CREATE INDEX warnings_2015_combo_idx on 
	warnings_2015(wfo, phenomena, eventid, significance);
CREATE INDEX warnings_2015_expire_idx on warnings_2015(expire);
CREATE INDEX warnings_2015_gtype_idx on warnings_2015(gtype);
CREATE INDEX warnings_2015_issue_idx on warnings_2015(issue);
CREATE INDEX warnings_2015_ugc_idx on warnings_2015(ugc);
CREATE INDEX warnings_2015_wfo_idx on warnings_2015(wfo);
grant select on warnings_2015 to nobody,apache;

CREATE table sbw_2015() inherits (sbw);
create index sbw_2015_idx on sbw_2015(wfo,eventid,significance,phenomena);
create index sbw_2015_expire_idx on sbw_2015(expire);
create index sbw_2015_issue_idx on sbw_2015(issue);
create index sbw_2015_wfo_idx on sbw_2015(wfo);
grant select on sbw_2015 to apache,nobody;
