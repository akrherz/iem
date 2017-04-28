-- Storage of webcam full resolution
ALTER TABLE webcams
  ADD fullres varchar(9) DEFAULT '640x480' NOT NULL;
