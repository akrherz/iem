CREATE TABLE ffg_2019(
  CONSTRAINT __ffg_2019_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (ffg);
CREATE INDEX ffg_2019_ugc_idx on ffg_2019(ugc);
CREATE INDEX ffg_2019_valid_idx on ffg_2019(valid);
GRANT ALL on ffg_2019 to ldm,mesonet;
GRANT SELECT on ffg_2019 to nobody,apache;

CREATE TABLE nldn2019_01(
  CONSTRAINT __nldn2019_01_check 
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2019-02-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_01_valid_idx on nldn2019_01(valid);
GRANT ALL on nldn2019_01 to ldm,mesonet;
GRANT SELECT on nldn2019_01 to nobody,apache;
    
CREATE TABLE nldn2019_02(
  CONSTRAINT __nldn2019_02_check 
  CHECK(valid >= '2019-02-01 00:00+00'::timestamptz
        and valid < '2019-03-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_02_valid_idx on nldn2019_02(valid);
GRANT ALL on nldn2019_02 to ldm,mesonet;
GRANT SELECT on nldn2019_02 to nobody,apache;
    
CREATE TABLE nldn2019_03(
  CONSTRAINT __nldn2019_03_check 
  CHECK(valid >= '2019-03-01 00:00+00'::timestamptz
        and valid < '2019-04-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_03_valid_idx on nldn2019_03(valid);
GRANT ALL on nldn2019_03 to ldm,mesonet;
GRANT SELECT on nldn2019_03 to nobody,apache;
    
CREATE TABLE nldn2019_04(
  CONSTRAINT __nldn2019_04_check 
  CHECK(valid >= '2019-04-01 00:00+00'::timestamptz
        and valid < '2019-05-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_04_valid_idx on nldn2019_04(valid);
GRANT ALL on nldn2019_04 to ldm,mesonet;
GRANT SELECT on nldn2019_04 to nobody,apache;
    
CREATE TABLE nldn2019_05(
  CONSTRAINT __nldn2019_05_check 
  CHECK(valid >= '2019-05-01 00:00+00'::timestamptz
        and valid < '2019-06-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_05_valid_idx on nldn2019_05(valid);
GRANT ALL on nldn2019_05 to ldm,mesonet;
GRANT SELECT on nldn2019_05 to nobody,apache;
    
CREATE TABLE nldn2019_06(
  CONSTRAINT __nldn2019_06_check 
  CHECK(valid >= '2019-06-01 00:00+00'::timestamptz
        and valid < '2019-07-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_06_valid_idx on nldn2019_06(valid);
GRANT ALL on nldn2019_06 to ldm,mesonet;
GRANT SELECT on nldn2019_06 to nobody,apache;
    
CREATE TABLE nldn2019_07(
  CONSTRAINT __nldn2019_07_check 
  CHECK(valid >= '2019-07-01 00:00+00'::timestamptz
        and valid < '2019-08-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_07_valid_idx on nldn2019_07(valid);
GRANT ALL on nldn2019_07 to ldm,mesonet;
GRANT SELECT on nldn2019_07 to nobody,apache;
    
CREATE TABLE nldn2019_08(
  CONSTRAINT __nldn2019_08_check 
  CHECK(valid >= '2019-08-01 00:00+00'::timestamptz
        and valid < '2019-09-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_08_valid_idx on nldn2019_08(valid);
GRANT ALL on nldn2019_08 to ldm,mesonet;
GRANT SELECT on nldn2019_08 to nobody,apache;
    
CREATE TABLE nldn2019_09(
  CONSTRAINT __nldn2019_09_check 
  CHECK(valid >= '2019-09-01 00:00+00'::timestamptz
        and valid < '2019-10-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_09_valid_idx on nldn2019_09(valid);
GRANT ALL on nldn2019_09 to ldm,mesonet;
GRANT SELECT on nldn2019_09 to nobody,apache;
    
CREATE TABLE nldn2019_10(
  CONSTRAINT __nldn2019_10_check 
  CHECK(valid >= '2019-10-01 00:00+00'::timestamptz
        and valid < '2019-11-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_10_valid_idx on nldn2019_10(valid);
GRANT ALL on nldn2019_10 to ldm,mesonet;
GRANT SELECT on nldn2019_10 to nobody,apache;
    
CREATE TABLE nldn2019_11(
  CONSTRAINT __nldn2019_11_check 
  CHECK(valid >= '2019-11-01 00:00+00'::timestamptz
        and valid < '2019-12-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_11_valid_idx on nldn2019_11(valid);
GRANT ALL on nldn2019_11 to ldm,mesonet;
GRANT SELECT on nldn2019_11 to nobody,apache;
    
CREATE TABLE nldn2019_12(
  CONSTRAINT __nldn2019_12_check 
  CHECK(valid >= '2019-12-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (nldn_all);
CREATE INDEX nldn2019_12_valid_idx on nldn2019_12(valid);
GRANT ALL on nldn2019_12 to ldm,mesonet;
GRANT SELECT on nldn2019_12 to nobody,apache;

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
