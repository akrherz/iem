-- Storage of new editedby column
ALTER TABLE pesticides add editedby varchar;
ALTER TABLE management add editedby varchar;
ALTER TABLE operations add editedby varchar;