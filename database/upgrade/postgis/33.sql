-- Storage of computed sounding parameters
ALTER TABLE raob_flights add sbcape_jkg real;
ALTER TABLE raob_flights add mucape_jkg real;
ALTER TABLE raob_flights add pwater_mm real;
ALTER TABLE raob_flights add sbcin_jkg real;
ALTER TABLE raob_flights add mucin_jkg real;
ALTER TABLE raob_flights add computed boolean DEFAULT 'f';
