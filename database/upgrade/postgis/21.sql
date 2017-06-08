-- Numeric prioritization of SPC Outlook Thresholds
CREATE TABLE spc_outlook_thresholds(
  priority smallint UNIQUE,
  threshold varchar(4));
GRANT SELECT on spc_outlook_thresholds to nobody,apache;
GRANT ALL on spc_outlook_thresholds to ldm,mesonet;

INSERT into spc_outlook_thresholds VALUES 
 (10, '0.02'),
 (20, '0.05'),
 (30, '0.10'),
 (40, '0.15'),
 (50, '0.25'),
 (60, '0.30'),
 (70, '0.35'),
 (80, '0.40'),
 (90, '0.45'),
 (100, '0.60'),
 (110, 'TSTM'),
 (120, 'MRGL'),
 (130, 'SLGT'),
 (140, 'ENH'),
 (150, 'MDT'),
 (160, 'HIGH'),
 (170, 'CRIT'),
 (180, 'EXTM');
