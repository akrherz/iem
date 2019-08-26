

CREATE TABLE nldn2017_01(
  CONSTRAINT __nldn2017_01_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
        and valid < '2017-02-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_01_valid_idx on nldn2017_01(valid);
GRANT ALL on nldn2017_01 to ldm,mesonet;
GRANT SELECT on nldn2017_01 to nobody,apache;
    
CREATE TABLE nldn2017_02(
  CONSTRAINT __nldn2017_02_check 
  CHECK(valid >= '2017-02-01 00:00+00'::timestamptz
        and valid < '2017-03-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_02_valid_idx on nldn2017_02(valid);
GRANT ALL on nldn2017_02 to ldm,mesonet;
GRANT SELECT on nldn2017_02 to nobody,apache;
    
CREATE TABLE nldn2017_03(
  CONSTRAINT __nldn2017_03_check 
  CHECK(valid >= '2017-03-01 00:00+00'::timestamptz
        and valid < '2017-04-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_03_valid_idx on nldn2017_03(valid);
GRANT ALL on nldn2017_03 to ldm,mesonet;
GRANT SELECT on nldn2017_03 to nobody,apache;
    
CREATE TABLE nldn2017_04(
  CONSTRAINT __nldn2017_04_check 
  CHECK(valid >= '2017-04-01 00:00+00'::timestamptz
        and valid < '2017-05-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_04_valid_idx on nldn2017_04(valid);
GRANT ALL on nldn2017_04 to ldm,mesonet;
GRANT SELECT on nldn2017_04 to nobody,apache;
    
CREATE TABLE nldn2017_05(
  CONSTRAINT __nldn2017_05_check 
  CHECK(valid >= '2017-05-01 00:00+00'::timestamptz
        and valid < '2017-06-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_05_valid_idx on nldn2017_05(valid);
GRANT ALL on nldn2017_05 to ldm,mesonet;
GRANT SELECT on nldn2017_05 to nobody,apache;
    
CREATE TABLE nldn2017_06(
  CONSTRAINT __nldn2017_06_check 
  CHECK(valid >= '2017-06-01 00:00+00'::timestamptz
        and valid < '2017-07-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_06_valid_idx on nldn2017_06(valid);
GRANT ALL on nldn2017_06 to ldm,mesonet;
GRANT SELECT on nldn2017_06 to nobody,apache;
    
CREATE TABLE nldn2017_07(
  CONSTRAINT __nldn2017_07_check 
  CHECK(valid >= '2017-07-01 00:00+00'::timestamptz
        and valid < '2017-08-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_07_valid_idx on nldn2017_07(valid);
GRANT ALL on nldn2017_07 to ldm,mesonet;
GRANT SELECT on nldn2017_07 to nobody,apache;
    
CREATE TABLE nldn2017_08(
  CONSTRAINT __nldn2017_08_check 
  CHECK(valid >= '2017-08-01 00:00+00'::timestamptz
        and valid < '2017-09-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_08_valid_idx on nldn2017_08(valid);
GRANT ALL on nldn2017_08 to ldm,mesonet;
GRANT SELECT on nldn2017_08 to nobody,apache;
    
CREATE TABLE nldn2017_09(
  CONSTRAINT __nldn2017_09_check 
  CHECK(valid >= '2017-09-01 00:00+00'::timestamptz
        and valid < '2017-10-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_09_valid_idx on nldn2017_09(valid);
GRANT ALL on nldn2017_09 to ldm,mesonet;
GRANT SELECT on nldn2017_09 to nobody,apache;
    
CREATE TABLE nldn2017_10(
  CONSTRAINT __nldn2017_10_check 
  CHECK(valid >= '2017-10-01 00:00+00'::timestamptz
        and valid < '2017-11-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_10_valid_idx on nldn2017_10(valid);
GRANT ALL on nldn2017_10 to ldm,mesonet;
GRANT SELECT on nldn2017_10 to nobody,apache;
    
CREATE TABLE nldn2017_11(
  CONSTRAINT __nldn2017_11_check 
  CHECK(valid >= '2017-11-01 00:00+00'::timestamptz
        and valid < '2017-12-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_11_valid_idx on nldn2017_11(valid);
GRANT ALL on nldn2017_11 to ldm,mesonet;
GRANT SELECT on nldn2017_11 to nobody,apache;
    
CREATE TABLE nldn2017_12(
  CONSTRAINT __nldn2017_12_check 
  CHECK(valid >= '2017-12-01 00:00+00'::timestamptz
        and valid < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2017_12_valid_idx on nldn2017_12(valid);
GRANT ALL on nldn2017_12 to ldm,mesonet;
GRANT SELECT on nldn2017_12 to nobody,apache;

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
