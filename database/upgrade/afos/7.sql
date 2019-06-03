-- ________________________________________________________________
create table products_1993_0106(
  CONSTRAINT __products19930106_check
  CHECK(entered >= '1993-01-01 00:00+00'::timestamptz
        and entered < '1993-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1993_0106_pil_idx on products_1993_0106(pil);
CREATE INDEX products_1993_0106_entered_idx on products_1993_0106(entered);
CREATE INDEX products_1993_0106_source_idx on products_1993_0106(source);
create index products_1993_0106_pe_idx on products_1993_0106(pil, entered);
GRANT all on products_1993_0106 to mesonet,ldm;
grant select on products_1993_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1993_0712(
  CONSTRAINT __products19930712_check
  CHECK(entered >= '1993-07-01 00:00+00'::timestamptz
        and entered < '1994-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1993_0712_pil_idx on products_1993_0712(pil);
CREATE INDEX products_1993_0712_entered_idx on products_1993_0712(entered);
CREATE INDEX products_1993_0712_source_idx on products_1993_0712(source); 
create index products_1993_0712_pe_idx on products_1993_0712(pil, entered);
GRANT all on products_1993_0712 to mesonet,ldm;
grant select on products_1993_0712 to nobody,apache;

-- ________________________________________________________________
create table products_1994_0106(
  CONSTRAINT __products19940106_check
  CHECK(entered >= '1994-01-01 00:00+00'::timestamptz
        and entered < '1994-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1994_0106_pil_idx on products_1994_0106(pil);
CREATE INDEX products_1994_0106_entered_idx on products_1994_0106(entered);
CREATE INDEX products_1994_0106_source_idx on products_1994_0106(source);
create index products_1994_0106_pe_idx on products_1994_0106(pil, entered);
GRANT all on products_1994_0106 to mesonet,ldm;
grant select on products_1994_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1994_0712(
  CONSTRAINT __products19940712_check
  CHECK(entered >= '1994-07-01 00:00+00'::timestamptz
        and entered < '1995-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1994_0712_pil_idx on products_1994_0712(pil);
CREATE INDEX products_1994_0712_entered_idx on products_1994_0712(entered);
CREATE INDEX products_1994_0712_source_idx on products_1994_0712(source); 
create index products_1994_0712_pe_idx on products_1994_0712(pil, entered);
GRANT all on products_1994_0712 to mesonet,ldm;
grant select on products_1994_0712 to nobody,apache;

-- ________________________________________________________________
create table products_1995_0106(
  CONSTRAINT __products19950106_check
  CHECK(entered >= '1995-01-01 00:00+00'::timestamptz
        and entered < '1995-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1995_0106_pil_idx on products_1995_0106(pil);
CREATE INDEX products_1995_0106_entered_idx on products_1995_0106(entered);
CREATE INDEX products_1995_0106_source_idx on products_1995_0106(source);
create index products_1995_0106_pe_idx on products_1995_0106(pil, entered);
GRANT all on products_1995_0106 to mesonet,ldm;
grant select on products_1995_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1995_0712(
  CONSTRAINT __products19950712_check
  CHECK(entered >= '1995-07-01 00:00+00'::timestamptz
        and entered < '1996-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1995_0712_pil_idx on products_1995_0712(pil);
CREATE INDEX products_1995_0712_entered_idx on products_1995_0712(entered);
CREATE INDEX products_1995_0712_source_idx on products_1995_0712(source); 
create index products_1995_0712_pe_idx on products_1995_0712(pil, entered);
GRANT all on products_1995_0712 to mesonet,ldm;
grant select on products_1995_0712 to nobody,apache;
