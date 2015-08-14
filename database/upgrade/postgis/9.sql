-- Remove unused column
ALTER TABLE warnings DROP fips;

-- Add some proper constraints to keep database cleaner
alter table warnings_2015 ADD CONSTRAINT warnings_2015_gid_fkey 
	FOREIGN KEY(gid) REFERENCES ugcs(gid);
alter table warnings_2015 ALTER issue SET NOT NULL;
alter table warnings_2015 ALTER expire SET NOT NULL;
alter table warnings_2015 ALTER updated SET NOT NULL;
alter table warnings_2015 ALTER WFO SET NOT NULL;
alter table warnings_2015 ALTER eventid SET NOT NULL;
alter table warnings_2015 ALTER status SET NOT NULL;
alter table warnings_2015 ALTER ugc SET NOT NULL;
alter table warnings_2015 ALTER phenomena SET NOT NULL;
alter table warnings_2015 ALTER significance SET NOT NULL;
alter table warnings_2015 ALTER init_expire SET NOT NULL;
alter table warnings_2015 ALTER product_issue SET NOT NULL;
