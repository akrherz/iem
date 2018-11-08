-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (9, now());

-- Storage of USCRN sub-hourly data

CREATE TABLE uscrn_alldata(
  station varchar(5),
  valid timestamptz,
  tmpc real,
  precip_mm real,
  srad real,
  srad_flag char(1),
  skinc real,
  skinc_flag char(1),
  skinc_type char(1),
  rh real,
  rh_flag real,
  vsm5 real,
  soilc5 real,
  wetness real,
  wetness_flag char(1),
  wind_mps real,
  wind_mps_flag char(1));
GRANT SELECT on uscrn_alldata to nobody,apache;
GRANT ALL on uscrn_alldata to mesonet,ldm;

create table uscrn_t2006( 
  CONSTRAINT __t2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2006_station_idx on uscrn_t2006(station);
CREATE INDEX uscrn_t2006_valid_idx on uscrn_t2006(valid);
GRANT SELECT on uscrn_t2006 to nobody,apache;
GRANT ALL on uscrn_t2006 to ldm,mesonet;
    

create table uscrn_t2007( 
  CONSTRAINT __t2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2007_station_idx on uscrn_t2007(station);
CREATE INDEX uscrn_t2007_valid_idx on uscrn_t2007(valid);
GRANT SELECT on uscrn_t2007 to nobody,apache;
GRANT ALL on uscrn_t2007 to ldm,mesonet;
    

create table uscrn_t2008( 
  CONSTRAINT __t2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2008_station_idx on uscrn_t2008(station);
CREATE INDEX uscrn_t2008_valid_idx on uscrn_t2008(valid);
GRANT SELECT on uscrn_t2008 to nobody,apache;
GRANT ALL on uscrn_t2008 to ldm,mesonet;
    

create table uscrn_t2009( 
  CONSTRAINT __t2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2009_station_idx on uscrn_t2009(station);
CREATE INDEX uscrn_t2009_valid_idx on uscrn_t2009(valid);
GRANT SELECT on uscrn_t2009 to nobody,apache;
GRANT ALL on uscrn_t2009 to ldm,mesonet;
    

create table uscrn_t2010( 
  CONSTRAINT __t2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2010_station_idx on uscrn_t2010(station);
CREATE INDEX uscrn_t2010_valid_idx on uscrn_t2010(valid);
GRANT SELECT on uscrn_t2010 to nobody,apache;
GRANT ALL on uscrn_t2010 to ldm,mesonet;
    

create table uscrn_t2011( 
  CONSTRAINT __t2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2011_station_idx on uscrn_t2011(station);
CREATE INDEX uscrn_t2011_valid_idx on uscrn_t2011(valid);
GRANT SELECT on uscrn_t2011 to nobody,apache;
GRANT ALL on uscrn_t2011 to ldm,mesonet;
    

create table uscrn_t2012( 
  CONSTRAINT __t2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2012_station_idx on uscrn_t2012(station);
CREATE INDEX uscrn_t2012_valid_idx on uscrn_t2012(valid);
GRANT SELECT on uscrn_t2012 to nobody,apache;
GRANT ALL on uscrn_t2012 to ldm,mesonet;
    

create table uscrn_t2013( 
  CONSTRAINT __t2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2013_station_idx on uscrn_t2013(station);
CREATE INDEX uscrn_t2013_valid_idx on uscrn_t2013(valid);
GRANT SELECT on uscrn_t2013 to nobody,apache;
GRANT ALL on uscrn_t2013 to ldm,mesonet;
    

create table uscrn_t2014( 
  CONSTRAINT __t2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2014_station_idx on uscrn_t2014(station);
CREATE INDEX uscrn_t2014_valid_idx on uscrn_t2014(valid);
GRANT SELECT on uscrn_t2014 to nobody,apache;
GRANT ALL on uscrn_t2014 to ldm,mesonet;
    

create table uscrn_t2015( 
  CONSTRAINT __t2015_check 
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz 
        and valid < '2016-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2015_station_idx on uscrn_t2015(station);
CREATE INDEX uscrn_t2015_valid_idx on uscrn_t2015(valid);
GRANT SELECT on uscrn_t2015 to nobody,apache;
GRANT ALL on uscrn_t2015 to ldm,mesonet;
    

create table uscrn_t2016( 
  CONSTRAINT __t2016_check 
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz 
        and valid < '2017-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2016_station_idx on uscrn_t2016(station);
CREATE INDEX uscrn_t2016_valid_idx on uscrn_t2016(valid);
GRANT SELECT on uscrn_t2016 to nobody,apache;
GRANT ALL on uscrn_t2016 to ldm,mesonet;
    

create table uscrn_t2017( 
  CONSTRAINT __t2017_check 
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz 
        and valid < '2018-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2017_station_idx on uscrn_t2017(station);
CREATE INDEX uscrn_t2017_valid_idx on uscrn_t2017(valid);
GRANT SELECT on uscrn_t2017 to nobody,apache;
GRANT ALL on uscrn_t2017 to ldm,mesonet;
    

create table uscrn_t2018( 
  CONSTRAINT __t2018_check 
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz 
        and valid < '2019-01-01 00:00+00')) 
  INHERITS (uscrn_alldata);
CREATE INDEX uscrn_t2018_station_idx on uscrn_t2018(station);
CREATE INDEX uscrn_t2018_valid_idx on uscrn_t2018(valid);
GRANT SELECT on uscrn_t2018 to nobody,apache;
GRANT ALL on uscrn_t2018 to ldm,mesonet;
    


---
--- Stuart Smith Park Hydrology Learning Lab
---
CREATE TABLE ss_bubbler(
  valid timestamptz,
  field varchar(32),
  value real,
  units varchar(32)
);
CREATE INDEX ss_bubbler_idx on ss_bubbler(valid);
GRANT SELECT on ss_bubbler to nobody,apache;

---
--- Stuart Smith Park Hydrology Learning Lab
---
CREATE TABLE ss_logger_data(
  id int,
  site_serial int,
  valid timestamptz,
  ch1_data_p real,
  ch2_data_p real,
  ch3_data_p real,
  ch4_data_p real,
  ch1_data_t real,
  ch2_data_t real,
  ch3_data_t real,
  ch4_data_t real,
  ch1_data_c real,
  ch2_data_c real,
  ch3_data_c real,
  ch4_data_c real
);
CREATE INDEX ss_logger_data_idx on ss_logger_data(valid);
GRANT SELECT on ss_logger_data to nobody,apache;

CREATE TABLE asi_data (
  station char(7),
  valid timestamp with time zone,
  ch1avg real,
  ch1sd  real,
  ch1max real,
  ch1min real,
  ch2avg real,
  ch2sd  real,
  ch2max real,
  ch2min real,
  ch3avg real,
  ch3sd  real,
  ch3max real,
  ch3min real,
  ch4avg real,
  ch4sd  real,
  ch4max real,
  ch4min real,
  ch5avg real,
  ch5sd  real,
  ch5max real,
  ch5min real,
  ch6avg real,
  ch6sd  real,
  ch6max real,
  ch6min real,
  ch7avg real,
  ch7sd  real,
  ch7max real,
  ch7min real,
  ch8avg real,
  ch8sd  real,
  ch8max real,
  ch8min real,
  ch9avg real,
  ch9sd  real,
  ch9max real,
  ch9min real,
  ch10avg real,
  ch10sd  real,
  ch10max real,
  ch10min real,
  ch11avg real,
  ch11sd  real,
  ch11max real,
  ch11min real,
  ch12avg real,
  ch12sd  real,
  ch12max real,
  ch12min real);
CREATE unique index asi_data_idx on asi_data(station, valid);
GRANT SELECT on asi_data to nobody;
GRANT SELECT on asi_data to apache;
  

CREATE TABLE alldata (
    station character varying(6),
    valid timestamp with time zone,
    tmpf real,
    dwpf real,
    drct real,
    sknt real,
    gust real,
    relh real,
    alti real,
    pcpncnt real,
    pday real,
    pmonth real,
    srad real,
    c1tmpf real
);
create table t2003( 
  CONSTRAINT __t2003_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2003_idx on t2003(station, valid);
GRANT SELECT on t2003 to nobody,apache;
    

create table t2004( 
  CONSTRAINT __t2004_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2004_idx on t2004(station, valid);
GRANT SELECT on t2004 to nobody,apache;
    

create table t2005( 
  CONSTRAINT __t2005_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2005_idx on t2005(station, valid);
GRANT SELECT on t2005 to nobody,apache;
    

create table t2006( 
  CONSTRAINT __t2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2006_idx on t2006(station, valid);
GRANT SELECT on t2006 to nobody,apache;
    

create table t2007( 
  CONSTRAINT __t2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2007_idx on t2007(station, valid);
GRANT SELECT on t2007 to nobody,apache;
    

create table t2008( 
  CONSTRAINT __t2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2008_idx on t2008(station, valid);
GRANT SELECT on t2008 to nobody,apache;
    

create table t2009( 
  CONSTRAINT __t2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2009_idx on t2009(station, valid);
GRANT SELECT on t2009 to nobody,apache;
    

create table t2010( 
  CONSTRAINT __t2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2010_idx on t2010(station, valid);
GRANT SELECT on t2010 to nobody,apache;
    

create table t2011( 
  CONSTRAINT __t2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2011_idx on t2011(station, valid);
GRANT SELECT on t2011 to nobody,apache;
    

create table t2012( 
  CONSTRAINT __t2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2012_idx on t2012(station, valid);
GRANT SELECT on t2012 to nobody,apache;
    

create table t2013( 
  CONSTRAINT __t2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2013_idx on t2013(station, valid);
GRANT SELECT on t2013 to nobody,apache;

create table t2014( 
  CONSTRAINT __t2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (alldata);
CREATE INDEX t2014_idx on t2014(station, valid);
GRANT SELECT on t2014 to nobody,apache;

CREATE TABLE flux_data(
station            character varying(10),   
 valid             timestamp with time zone,
 fc_wpl            real,
 le_wpl            real,
 hs                real,
 tau               real,
 u_star            real,
 cov_uz_uz         real,
 cov_uz_ux         real,
 cov_uz_uy         real,
 cov_uz_co2        real,
 cov_uz_h2o        real,
 cov_uz_ts         real,
 cov_ux_ux         real,
 cov_ux_uy         real,
 cov_ux_co2        real,
 cov_ux_h2o        real,
 cov_ux_ts         real,
 cov_uy_uy         real,
 cov_uy_co2        real,
 cov_uy_h2o        real,
 cov_uy_ts         real,
 cov_co2_co2       real,
 cov_h2o_h2o       real,
 cov_ts_ts         real,
 ux_avg            real,
 uy_avg            real,
 uz_avg            real,
 co2_avg           real,
 h2o_avg           real,
 ts_avg            real,
 rho_a_avg         real,
 press_avg         real,
 panel_temp_avg    real,
 wnd_dir_compass   real,
 wnd_dir_csat3     real,
 wnd_spd           real,
 rslt_wnd_spd      real,
 batt_volt_avg     real,
 std_wnd_dir       real,
 fc_irga           real,
 le_irga           real,
 co2_wpl_le        real,
 co2_wpl_h         real,
 h2o_wpl_le        real,
 h2o_wpl_h         real,
 h2o_hmp_avg       real,
 t_hmp_avg         real,
 par_avg           real,
 solrad_avg        real,
 rain_tot          real,
 shf1_avg          real,
 shf2_avg          real,
 soiltc1_avg       real,
 soiltc2_avg       real,
 soiltc3_avg       real,
 soiltc4_avg       real,
 irt_can_avg       real,
 irt_cb_avg        real,
 incoming_sw       real,
 outgoing_sw       real,
 incoming_lw_tcor  real,
 terrest_lw_tcor   real,
 rn_short_avg      real,
 rn_long_avg       real,
 rn_total_avg      real,
 rh_hmp_avg        real,
 temps_c1_avg      real,
 corrtemp_avg      real,
 rn_total_tcor_avg real,
 incoming_lw_avg   real,
 terrestrial_lw_avg real,
 wfv1_avg          real,
 n_tot real,
 csat_warnings real,
 irga_warnings real,
 del_t_f_tot real,
 track_f_tot real,
 amp_h_f_tot real,
 amp_l_f_tot real,
 chopper_f_tot real,
 detector_f_tot real,
 pll_f_tot real,
 sync_f_tot real, 
 agc_avg real, 
 solarrad_mv_avg real, 
 solarrad_w_avg real, 
 par_mv_avg real, 
 par_den_avg real,
 surftc_avg real, 
 temp_c1_avg real,
 temp_k1_avg real,
 irr_can_corr_avg real,
 irr_body_avg real,
 vwc real,
 ec real,
 t real,
 p real,
 pa real,
 vr real
);
GRANT SELECT on flux_data to nobody,apache;

create table flux2002( 
  CONSTRAINT __flux2002_check 
  CHECK(valid >= '2002-01-01 00:00+00'::timestamptz 
        and valid < '2003-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2002_idx on flux2002(station, valid);
GRANT SELECT on flux2002 to nobody,apache;
    

create table flux2003( 
  CONSTRAINT __flux2003_check 
  CHECK(valid >= '2003-01-01 00:00+00'::timestamptz 
        and valid < '2004-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2003_idx on flux2003(station, valid);
GRANT SELECT on flux2003 to nobody,apache;
    

create table flux2004( 
  CONSTRAINT __flux2004_check 
  CHECK(valid >= '2004-01-01 00:00+00'::timestamptz 
        and valid < '2005-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2004_idx on flux2004(station, valid);
GRANT SELECT on flux2004 to nobody,apache;
    

create table flux2005( 
  CONSTRAINT __flux2005_check 
  CHECK(valid >= '2005-01-01 00:00+00'::timestamptz 
        and valid < '2006-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2005_idx on flux2005(station, valid);
GRANT SELECT on flux2005 to nobody,apache;
    

create table flux2006( 
  CONSTRAINT __flux2006_check 
  CHECK(valid >= '2006-01-01 00:00+00'::timestamptz 
        and valid < '2007-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2006_idx on flux2006(station, valid);
GRANT SELECT on flux2006 to nobody,apache;
    

create table flux2007( 
  CONSTRAINT __flux2007_check 
  CHECK(valid >= '2007-01-01 00:00+00'::timestamptz 
        and valid < '2008-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2007_idx on flux2007(station, valid);
GRANT SELECT on flux2007 to nobody,apache;
    

create table flux2008( 
  CONSTRAINT __flux2008_check 
  CHECK(valid >= '2008-01-01 00:00+00'::timestamptz 
        and valid < '2009-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2008_idx on flux2008(station, valid);
GRANT SELECT on flux2008 to nobody,apache;
    

create table flux2009( 
  CONSTRAINT __flux2009_check 
  CHECK(valid >= '2009-01-01 00:00+00'::timestamptz 
        and valid < '2010-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2009_idx on flux2009(station, valid);
GRANT SELECT on flux2009 to nobody,apache;
    

create table flux2010( 
  CONSTRAINT __flux2010_check 
  CHECK(valid >= '2010-01-01 00:00+00'::timestamptz 
        and valid < '2011-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2010_idx on flux2010(station, valid);
GRANT SELECT on flux2010 to nobody,apache;
    

create table flux2011( 
  CONSTRAINT __flux2011_check 
  CHECK(valid >= '2011-01-01 00:00+00'::timestamptz 
        and valid < '2012-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2011_idx on flux2011(station, valid);
GRANT SELECT on flux2011 to nobody,apache;
    

create table flux2012( 
  CONSTRAINT __flux2012_check 
  CHECK(valid >= '2012-01-01 00:00+00'::timestamptz 
        and valid < '2013-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2012_idx on flux2012(station, valid);
GRANT SELECT on flux2012 to nobody,apache;
    

create table flux2013( 
  CONSTRAINT __flux2013_check 
  CHECK(valid >= '2013-01-01 00:00+00'::timestamptz 
        and valid < '2014-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2013_idx on flux2013(station, valid);
GRANT SELECT on flux2013 to nobody,apache;


create table flux2014( 
  CONSTRAINT __flux2014_check 
  CHECK(valid >= '2014-01-01 00:00+00'::timestamptz 
        and valid < '2015-01-01 00:00+00')) 
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2014_idx on flux2014(station, valid);
GRANT SELECT on flux2014 to nobody,apache;

create table t2015(
  CONSTRAINT __t2015_check
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz
        and valid < '2016-01-01 00:00+00'))
  INHERITS (alldata);
CREATE UNIQUE INDEX t2015_idx on t2015(station, valid);
GRANT SELECT on t2015 to nobody,apache;

create table flux2015(
  CONSTRAINT __flux2015_check
  CHECK(valid >= '2015-01-01 00:00+00'::timestamptz
        and valid < '2016-01-01 00:00+00'))
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2015_idx on flux2015(station, valid);
GRANT SELECT on flux2015 to nobody,apache;

--
-- Storage of ISU FEEL Data
CREATE TABLE feel_data_daily(
        valid date UNIQUE,
        AirTemp_Max real,
        AirTemp_Min real,
        Rain_Tot real,
        Windspeed_Max real,
        SolarRad_MJ_Tot real
);
GRANT SELECT on feel_data_daily to nobody,apache;

CREATE TABLE feel_data_hourly(
        valid timestamptz UNIQUE,
        BattVolt_Avg real,
        PanTemp_Avg real,
        AirTemp_Avg real,
        RH_Avg real,
        sat_vp_Avg real,
        act_vp_Avg real,
        WindDir_Avg real,
        Windspeed_Avg real,
        SolarRad_mV_Avg real,
        SolarRad_W_Avg real,
        Soil_Temp_5_Avg real,
        Rain_Tot real,
        LWS1_Avg real,
        LWS2_Avg real,
        LWS3_Avg real,
        LWS1_Ohms real,
        LWS2_Ohms real,
        LWS3_Ohms real,
        LWS1_Ohms_Hst real,
        LWS2_Ohms_Hst real,
        LWS3_Ohms_Hst real
);
GRANT SELECT on feel_data_hourly to nobody,apache;

-- Storage of ncdc HPD data
--
CREATE TABLE hpd_alldata(
  station varchar(6),
  valid timestamptz,
  counter real,
  tmpc real,
  battery real,
  calc_precip real
);
GRANT SELECT on hpd_alldata to nobody,apache;

-- Individual years
CREATE TABLE hpd_2009(
	CONSTRAINT __hpd_2009_check
	CHECK(valid >= '2009-01-01 00:00+00'::timestamptz
	      and valid < '2010-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2009 to nobody,apache;
CREATE INDEX hpd_2009_station_idx on hpd_2009(station);

CREATE TABLE hpd_2010(
	CONSTRAINT __hpd_2010_check
	CHECK(valid >= '2010-01-01 00:00+00'::timestamptz
	      and valid < '2011-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2010 to nobody,apache;
CREATE INDEX hpd_2010_station_idx on hpd_2010(station);

CREATE TABLE hpd_2011(
	CONSTRAINT __hpd_2011_check
	CHECK(valid >= '2011-01-01 00:00+00'::timestamptz
	      and valid < '2012-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2011 to nobody,apache;
CREATE INDEX hpd_2011_station_idx on hpd_2011(station);

CREATE TABLE hpd_2012(
	CONSTRAINT __hpd_2012_check
	CHECK(valid >= '2012-01-01 00:00+00'::timestamptz
	      and valid < '2013-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2012 to nobody,apache;
CREATE INDEX hpd_2012_station_idx on hpd_2012(station);

CREATE TABLE hpd_2013(
	CONSTRAINT __hpd_2013_check
	CHECK(valid >= '2013-01-01 00:00+00'::timestamptz
	      and valid < '2014-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2013 to nobody,apache;
CREATE INDEX hpd_2013_station_idx on hpd_2013(station);

CREATE TABLE hpd_2014(
	CONSTRAINT __hpd_2014_check
	CHECK(valid >= '2014-01-01 00:00+00'::timestamptz
	      and valid < '2015-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2014 to nobody,apache;
CREATE INDEX hpd_2014_station_idx on hpd_2014(station);

CREATE TABLE hpd_2015(
	CONSTRAINT __hpd_2015_check
	CHECK(valid >= '2015-01-01 00:00+00'::timestamptz
	      and valid < '2016-01-01 00:00+00'::timestamptz)
	)
	INHERITS (hpd_alldata);
GRANT SELECT on hpd_2015 to nobody,apache;
CREATE INDEX hpd_2015_station_idx on hpd_2015(station);

create table t2016(
  CONSTRAINT __t2016_check
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz
        and valid < '2017-01-01 00:00+00'))
  INHERITS (alldata);
CREATE INDEX t2016_idx on t2016(station, valid);
GRANT SELECT on t2016 to nobody,apache;

create table flux2016(
  CONSTRAINT __flux2016_check
  CHECK(valid >= '2016-01-01 00:00+00'::timestamptz
        and valid < '2017-01-01 00:00+00'))
  INHERITS (flux_data);
CREATE INDEX flux2016_idx on flux2016(station, valid);
GRANT SELECT on flux2016 to nobody,apache;

CREATE TABLE hpd_2016(
        CONSTRAINT __hpd_2016_check
        CHECK(valid >= '2016-01-01 00:00+00'::timestamptz
              and valid < '2017-01-01 00:00+00'::timestamptz)
        )
        INHERITS (hpd_alldata);
GRANT SELECT on hpd_2016 to nobody,apache;
CREATE INDEX hpd_2016_station_idx on hpd_2016(station);

create table t2017(
  CONSTRAINT __t2017_check
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
        and valid < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2017_idx on t2017(station, valid);
GRANT SELECT on t2017 to nobody,apache;

create table flux2017(
  CONSTRAINT __flux2017_check
  CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
        and valid < '2018-01-01 00:00+00'::timestamptz))
  INHERITS (flux_data);
CREATE INDEX flux2017_idx on flux2017(station, valid);
GRANT SELECT on flux2017 to nobody,apache;

CREATE TABLE hpd_2017(
        CONSTRAINT __hpd_2017_check
        CHECK(valid >= '2017-01-01 00:00+00'::timestamptz
              and valid < '2018-01-01 00:00+00'::timestamptz)
        )
        INHERITS (hpd_alldata);
GRANT SELECT on hpd_2017 to nobody,apache;
CREATE INDEX hpd_2017_station_idx on hpd_2017(station);

---
create table t2018(
  CONSTRAINT __t2018_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2018_idx on t2018(station, valid);
GRANT SELECT on t2018 to nobody,apache;

create table flux2018(
  CONSTRAINT __flux2018_check
  CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
        and valid < '2019-01-01 00:00+00'::timestamptz))
  INHERITS (flux_data);
CREATE INDEX flux2018_idx on flux2018(station, valid);
GRANT SELECT on flux2018 to nobody,apache;

CREATE TABLE hpd_2018(
        CONSTRAINT __hpd_2018_check
        CHECK(valid >= '2018-01-01 00:00+00'::timestamptz
              and valid < '2019-01-01 00:00+00'::timestamptz)
        )
        INHERITS (hpd_alldata);
GRANT SELECT on hpd_2018 to nobody,apache;
CREATE INDEX hpd_2018_station_idx on hpd_2018(station);

create table t2019(
  CONSTRAINT __t2019_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (alldata);
CREATE INDEX t2019_idx on t2019(station, valid);
GRANT SELECT on t2019 to nobody,apache;

create table flux2019(
  CONSTRAINT __flux2019_check
  CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
        and valid < '2020-01-01 00:00+00'::timestamptz))
  INHERITS (flux_data);
CREATE UNIQUE INDEX flux2019_idx on flux2019(station, valid);
GRANT SELECT on flux2019 to nobody,apache;

CREATE TABLE hpd_2019(
        CONSTRAINT __hpd_2019_check
        CHECK(valid >= '2019-01-01 00:00+00'::timestamptz
              and valid < '2020-01-01 00:00+00'::timestamptz)
        )
        INHERITS (hpd_alldata);
GRANT SELECT on hpd_2019 to nobody,apache;
CREATE INDEX hpd_2019_station_idx on hpd_2019(station);
