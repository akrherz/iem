CREATE TABLE products(
  data text,
  pil char(6),
  entered timestamp with time zone,
  source char(4),
  wmo char(6)
);

CREATE TABLE products_2012_0106() inherits (products); 