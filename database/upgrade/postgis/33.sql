-- Storage of computed sounding parameters
ALTER TABLE raob_flights add sbcape_jkg real;
ALTER TABLE raob_flights add mucape_jkg real;
ALTER TABLE raob_flights add pwater_mm real;
ALTER TABLE raob_flights add sbcin_jkg real;
ALTER TABLE raob_flights add mucin_jkg real;
ALTER TABLE raob_flights add computed boolean DEFAULT 'f';
ALTER TABLE raob_flights add lcl_agl_m real;
ALTER TABLE raob_flights add lcl_pressure_hpa real;
ALTER TABLE raob_flights add lcl_tmpc real;
ALTER TABLE raob_flights add lfc_agl_m real;
ALTER TABLE raob_flights add lfc_pressure_hpa real;
ALTER TABLE raob_flights add lfc_tmpc real;
ALTER TABLE raob_flights add el_agl_m real;
ALTER TABLE raob_flights add el_pressure_hpa real;
ALTER TABLE raob_flights add el_tmpc real;
ALTER TABLE raob_flights add total_totals real;
ALTER TABLE raob_flights add sweat_index real;
