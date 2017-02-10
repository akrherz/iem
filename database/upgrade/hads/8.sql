-- Implement an alldata table, which the yearly tables will inherit
CREATE TABLE alldata(
  station varchar(8),
  valid timestamptz,
  key varchar(11),
  value real);
GRANT SELECT on alldata to nobody,apache;

alter table raw2002 inherit alldata;
alter table raw2003 inherit alldata;
alter table raw2004 inherit alldata;
alter table raw2005 inherit alldata;
alter table raw2006 inherit alldata;
alter table raw2007 inherit alldata;
alter table raw2008 inherit alldata;
alter table raw2009 inherit alldata;
alter table raw2010 inherit alldata;
alter table raw2011 inherit alldata;
alter table raw2012 inherit alldata;
alter table raw2013 inherit alldata;
alter table raw2014 inherit alldata;
alter table raw2015 inherit alldata;
alter table raw2016 inherit alldata;
alter table raw2017 inherit alldata;
