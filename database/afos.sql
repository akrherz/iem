CREATE TABLE products(
  data text,
  pil char(6),
  entered timestamptz,
  source char(4),
  wmo char(6)
);

create table products_2013_0106( 
  CONSTRAINT __products20130106_check 
  CHECK(entered >= '2013-01-01 00:00+00'::timestamptz 
        and entered < '2013-07-01 00:00+00')) 
  INHERITS (products);

CREATE INDEX products_2013_0106_pil_idx on products_2013_0106(pil);
CREATE INDEX products_2013_0106_entered_idx on products_2013_0106(entered);
CREATE INDEX products_2013_0106_source_idx on products_2013_0106(source);

grant select on products_2013_0106 to nobody,apache;