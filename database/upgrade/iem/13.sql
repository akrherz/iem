-- more proper wxcodes
ALTER TABLE current ADD wxcodes varchar(12)[];
ALTER TABLE current_log ADD wxcodes varchar(12)[];
ALTER TABLE current_tmp ADD wxcodes varchar(12)[];