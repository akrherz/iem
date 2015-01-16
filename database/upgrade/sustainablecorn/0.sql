--- Support additional columns in the Management Datastore

ALTER TABLE operations ADD plantryemethod varchar;
ALTER TABLE operations ADD plantmaturity varchar;
ALTER TABLE operations ADD growthstage varchar;
ALTER TABLE operations ADD canopyheight varchar;
ALTER TABLE operations ADD fertilizercrop varchar;

ALTER TABLE operations SET with OIDS;
ALTER TABLE management SET with OIDS;
ALTER TABLE pesticides SET with OIDS;
