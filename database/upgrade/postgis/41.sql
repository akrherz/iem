-- Storage of PDS tagged warnings
ALTER TABLE sbw add is_pds boolean;
ALTER TABLE warnings add is_pds boolean;