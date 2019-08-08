-- Allow filtering of active version inactive portfolios
ALTER TABLE portfolios add active boolean DEFAULT true;
UPDATE portfolios SET active = 't';
