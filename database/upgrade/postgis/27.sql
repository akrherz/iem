CREATE TABLE ffg_2018(
  CONSTRAINT __ffg_2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2018_ugc_idx on ffg_2018(ugc);
CREATE INDEX ffg_2018_valid_idx on ffg_2018(valid);
GRANT ALL on ffg_2018 to ldm,mesonet;
GRANT SELECT on ffg_2018 to nobody,apache;

CREATE TABLE nldn2018_01(
  CONSTRAINT __nldn2018_01_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2018-02-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_01_valid_idx on nldn2018_01(valid);
GRANT ALL on nldn2018_01 to ldm,mesonet;
GRANT SELECT on nldn2018_01 to nobody,apache;
    
CREATE TABLE nldn2018_02(
  CONSTRAINT __nldn2018_02_check 
  CHECK(valid >= '2018-02-01 00:00+00'::timestamptz
        and valid < '2018-03-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_02_valid_idx on nldn2018_02(valid);
GRANT ALL on nldn2018_02 to ldm,mesonet;
GRANT SELECT on nldn2018_02 to nobody,apache;
    
CREATE TABLE nldn2018_03(
  CONSTRAINT __nldn2018_03_check 
  CHECK(valid >= '2018-03-01 00:00+00'::timestamptz
        and valid < '2018-04-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_03_valid_idx on nldn2018_03(valid);
GRANT ALL on nldn2018_03 to ldm,mesonet;
GRANT SELECT on nldn2018_03 to nobody,apache;
    
CREATE TABLE nldn2018_04(
  CONSTRAINT __nldn2018_04_check 
  CHECK(valid >= '2018-04-01 00:00+00'::timestamptz
        and valid < '2018-05-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_04_valid_idx on nldn2018_04(valid);
GRANT ALL on nldn2018_04 to ldm,mesonet;
GRANT SELECT on nldn2018_04 to nobody,apache;
    
CREATE TABLE nldn2018_05(
  CONSTRAINT __nldn2018_05_check 
  CHECK(valid >= '2018-05-01 00:00+00'::timestamptz
        and valid < '2018-06-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_05_valid_idx on nldn2018_05(valid);
GRANT ALL on nldn2018_05 to ldm,mesonet;
GRANT SELECT on nldn2018_05 to nobody,apache;
    
CREATE TABLE nldn2018_06(
  CONSTRAINT __nldn2018_06_check 
  CHECK(valid >= '2018-06-01 00:00+00'::timestamptz
        and valid < '2018-07-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_06_valid_idx on nldn2018_06(valid);
GRANT ALL on nldn2018_06 to ldm,mesonet;
GRANT SELECT on nldn2018_06 to nobody,apache;
    
CREATE TABLE nldn2018_07(
  CONSTRAINT __nldn2018_07_check 
  CHECK(valid >= '2018-07-01 00:00+00'::timestamptz
        and valid < '2018-08-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_07_valid_idx on nldn2018_07(valid);
GRANT ALL on nldn2018_07 to ldm,mesonet;
GRANT SELECT on nldn2018_07 to nobody,apache;
    
CREATE TABLE nldn2018_08(
  CONSTRAINT __nldn2018_08_check 
  CHECK(valid >= '2018-08-01 00:00+00'::timestamptz
        and valid < '2018-09-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_08_valid_idx on nldn2018_08(valid);
GRANT ALL on nldn2018_08 to ldm,mesonet;
GRANT SELECT on nldn2018_08 to nobody,apache;
    
CREATE TABLE nldn2018_09(
  CONSTRAINT __nldn2018_09_check 
  CHECK(valid >= '2018-09-01 00:00+00'::timestamptz
        and valid < '2018-10-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_09_valid_idx on nldn2018_09(valid);
GRANT ALL on nldn2018_09 to ldm,mesonet;
GRANT SELECT on nldn2018_09 to nobody,apache;
    
CREATE TABLE nldn2018_10(
  CONSTRAINT __nldn2018_10_check 
  CHECK(valid >= '2018-10-01 00:00+00'::timestamptz
        and valid < '2018-11-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_10_valid_idx on nldn2018_10(valid);
GRANT ALL on nldn2018_10 to ldm,mesonet;
GRANT SELECT on nldn2018_10 to nobody,apache;
    
CREATE TABLE nldn2018_11(
  CONSTRAINT __nldn2018_11_check 
  CHECK(valid >= '2018-11-01 00:00+00'::timestamptz
        and valid < '2018-12-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_11_valid_idx on nldn2018_11(valid);
GRANT ALL on nldn2018_11 to ldm,mesonet;
GRANT SELECT on nldn2018_11 to nobody,apache;
    
CREATE TABLE nldn2018_12(
  CONSTRAINT __nldn2018_12_check 
  CHECK(valid >= '2018-12-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2018_12_valid_idx on nldn2018_12(valid);
GRANT ALL on nldn2018_12 to ldm,mesonet;
GRANT SELECT on nldn2018_12 to nobody,apache;

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
