--
-- Set cascading deletes when an entry is removed from the stations table
--
ALTER TABLE current
  DROP CONSTRAINT current_iemid_fkey,
  ADD CONSTRAINT current_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE current_log
  DROP CONSTRAINT current_log_iemid_fkey,
  ADD CONSTRAINT current_log_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE current_qc
  DROP CONSTRAINT current_qc_iemid_fkey,
  ADD CONSTRAINT current_qc_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE current_tmp
  DROP CONSTRAINT current_tmp_iemid_fkey,
  ADD CONSTRAINT current_tmp_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE events
  DROP CONSTRAINT events_iemid_fkey,
  ADD CONSTRAINT events_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE hourly
  DROP CONSTRAINT hourly_iemid_fkey,
  ADD CONSTRAINT hourly_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary_2014
  DROP CONSTRAINT summary_2014_iemid_fkey,
  ADD CONSTRAINT summary_2014_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary_2015
  DROP CONSTRAINT summary_2015_iemid_fkey,
  ADD CONSTRAINT summary_2015_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary
  DROP CONSTRAINT summary_iemid_fkey,
  ADD CONSTRAINT summary_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE trend_1h
  DROP CONSTRAINT trend_1h_iemid_fkey,
  ADD CONSTRAINT trend_1h_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;

ALTER TABLE summary_1941
  ADD CONSTRAINT summary_1941_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1942
  ADD CONSTRAINT summary_1942_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1943
  ADD CONSTRAINT summary_1943_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1944
  ADD CONSTRAINT summary_1944_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1945
  ADD CONSTRAINT summary_1945_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1946
  ADD CONSTRAINT summary_1946_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1947
  ADD CONSTRAINT summary_1947_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1948
  ADD CONSTRAINT summary_1948_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1949
  ADD CONSTRAINT summary_1949_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1950
  ADD CONSTRAINT summary_1950_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1951
  ADD CONSTRAINT summary_1951_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1952
  ADD CONSTRAINT summary_1952_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1953
  ADD CONSTRAINT summary_1953_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1954
  ADD CONSTRAINT summary_1954_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1955
  ADD CONSTRAINT summary_1955_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1956
  ADD CONSTRAINT summary_1956_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1957
  ADD CONSTRAINT summary_1957_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1958
  ADD CONSTRAINT summary_1958_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1959
  ADD CONSTRAINT summary_1959_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1960
  ADD CONSTRAINT summary_1960_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1961
  ADD CONSTRAINT summary_1961_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1962
  ADD CONSTRAINT summary_1962_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1963
  ADD CONSTRAINT summary_1963_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1964
  ADD CONSTRAINT summary_1964_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1965
  ADD CONSTRAINT summary_1965_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1966
  ADD CONSTRAINT summary_1966_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1967
  ADD CONSTRAINT summary_1967_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1968
  ADD CONSTRAINT summary_1968_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1969
  ADD CONSTRAINT summary_1969_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1970
  ADD CONSTRAINT summary_1970_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1971
  ADD CONSTRAINT summary_1971_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1972
  ADD CONSTRAINT summary_1972_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1973
  ADD CONSTRAINT summary_1973_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1974
  ADD CONSTRAINT summary_1974_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1975
  ADD CONSTRAINT summary_1975_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1976
  ADD CONSTRAINT summary_1976_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1977
  ADD CONSTRAINT summary_1977_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1978
  ADD CONSTRAINT summary_1978_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1979
  ADD CONSTRAINT summary_1979_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1980
  ADD CONSTRAINT summary_1980_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1981
  ADD CONSTRAINT summary_1981_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1982
  ADD CONSTRAINT summary_1982_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1983
  ADD CONSTRAINT summary_1983_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1984
  ADD CONSTRAINT summary_1984_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1985
  ADD CONSTRAINT summary_1985_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1986
  ADD CONSTRAINT summary_1986_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1987
  ADD CONSTRAINT summary_1987_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1988
  ADD CONSTRAINT summary_1988_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1989
  ADD CONSTRAINT summary_1989_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1990
  ADD CONSTRAINT summary_1990_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1991
  ADD CONSTRAINT summary_1991_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1992
  ADD CONSTRAINT summary_1992_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1993
  ADD CONSTRAINT summary_1993_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
ALTER TABLE summary_1994
  ADD CONSTRAINT summary_1994_iemid_fkey FOREIGN KEY (iemid)
  REFERENCES stations(iemid) ON DELETE CASCADE;
  