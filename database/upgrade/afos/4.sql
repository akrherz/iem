-- ________________________________________________________________
create table products_2018_0106(
  CONSTRAINT __products20180106_check
  CHECK(entered >= '2018-01-01 00:00+00'::timestamptz
        and entered < '2018-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2018_0106_pil_idx on products_2018_0106(pil);
CREATE INDEX products_2018_0106_entered_idx on products_2018_0106(entered);
CREATE INDEX products_2018_0106_source_idx on products_2018_0106(source);
create index products_2018_0106_pe_idx on products_2018_0106(pil, entered);
GRANT all on products_2018_0106 to mesonet,ldm;
grant select on products_2018_0106 to nobody,apache;

-- ________________________________________________________________
create table products_2018_0712(
  CONSTRAINT __products20180712_check
  CHECK(entered >= '2018-07-01 00:00+00'::timestamptz
        and entered < '2019-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_2018_0712_pil_idx on products_2018_0712(pil);
CREATE INDEX products_2018_0712_entered_idx on products_2018_0712(entered);
CREATE INDEX products_2018_0712_source_idx on products_2018_0712(source);
create index products_2018_0712_pe_idx on products_2018_0712(pil, entered);
GRANT all on products_2018_0712 to mesonet,ldm;
grant select on products_2018_0712 to nobody,apache;
