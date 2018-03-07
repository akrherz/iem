-- Storage of feature media type
ALTER TABLE feature ADD mediasuffix varchar(8) DEFAULT 'png';
-- Establish the default
UPDATE feature SET mediasuffix = 'png' where valid > '2010-02-19';
UPDATE feature SET mediasuffix = 'gif' where valid < '2010-02-19';
