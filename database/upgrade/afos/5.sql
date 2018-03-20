-- Gonna store more older products!
-- ________________________________________________________________
create table products_1996_0106(
  CONSTRAINT __products19960106_check
  CHECK(entered >= '1996-01-01 00:00+00'::timestamptz
        and entered < '1996-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1996_0106_pil_idx on products_1996_0106(pil);
CREATE INDEX products_1996_0106_entered_idx on products_1996_0106(entered);
CREATE INDEX products_1996_0106_source_idx on products_1996_0106(source);
create index products_1996_0106_pe_idx on products_1996_0106(pil, entered);
GRANT all on products_1996_0106 to mesonet,ldm;
grant select on products_1996_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1996_0712(
  CONSTRAINT __products19960712_check
  CHECK(entered >= '1996-07-01 00:00+00'::timestamptz
        and entered < '1997-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1996_0712_pil_idx on products_1996_0712(pil);
CREATE INDEX products_1996_0712_entered_idx on products_1996_0712(entered);
CREATE INDEX products_1996_0712_source_idx on products_1996_0712(source);
create index products_1996_0712_pe_idx on products_1996_0712(pil, entered);
GRANT all on products_1996_0712 to mesonet,ldm;
grant select on products_1996_0712 to nobody,apache;
    

-- ________________________________________________________________
create table products_1997_0106(
  CONSTRAINT __products19970106_check
  CHECK(entered >= '1997-01-01 00:00+00'::timestamptz
        and entered < '1997-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1997_0106_pil_idx on products_1997_0106(pil);
CREATE INDEX products_1997_0106_entered_idx on products_1997_0106(entered);
CREATE INDEX products_1997_0106_source_idx on products_1997_0106(source);
create index products_1997_0106_pe_idx on products_1997_0106(pil, entered);
GRANT all on products_1997_0106 to mesonet,ldm;
grant select on products_1997_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1997_0712(
  CONSTRAINT __products19970712_check
  CHECK(entered >= '1997-07-01 00:00+00'::timestamptz
        and entered < '1998-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1997_0712_pil_idx on products_1997_0712(pil);
CREATE INDEX products_1997_0712_entered_idx on products_1997_0712(entered);
CREATE INDEX products_1997_0712_source_idx on products_1997_0712(source);
create index products_1997_0712_pe_idx on products_1997_0712(pil, entered);
GRANT all on products_1997_0712 to mesonet,ldm;
grant select on products_1997_0712 to nobody,apache;
    

-- ________________________________________________________________
create table products_1998_0106(
  CONSTRAINT __products19980106_check
  CHECK(entered >= '1998-01-01 00:00+00'::timestamptz
        and entered < '1998-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1998_0106_pil_idx on products_1998_0106(pil);
CREATE INDEX products_1998_0106_entered_idx on products_1998_0106(entered);
CREATE INDEX products_1998_0106_source_idx on products_1998_0106(source);
create index products_1998_0106_pe_idx on products_1998_0106(pil, entered);
GRANT all on products_1998_0106 to mesonet,ldm;
grant select on products_1998_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1998_0712(
  CONSTRAINT __products19980712_check
  CHECK(entered >= '1998-07-01 00:00+00'::timestamptz
        and entered < '1999-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1998_0712_pil_idx on products_1998_0712(pil);
CREATE INDEX products_1998_0712_entered_idx on products_1998_0712(entered);
CREATE INDEX products_1998_0712_source_idx on products_1998_0712(source);
create index products_1998_0712_pe_idx on products_1998_0712(pil, entered);
GRANT all on products_1998_0712 to mesonet,ldm;
grant select on products_1998_0712 to nobody,apache;
    

-- ________________________________________________________________
create table products_1999_0106(
  CONSTRAINT __products19990106_check
  CHECK(entered >= '1999-01-01 00:00+00'::timestamptz
        and entered < '1999-07-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1999_0106_pil_idx on products_1999_0106(pil);
CREATE INDEX products_1999_0106_entered_idx on products_1999_0106(entered);
CREATE INDEX products_1999_0106_source_idx on products_1999_0106(source);
create index products_1999_0106_pe_idx on products_1999_0106(pil, entered);
GRANT all on products_1999_0106 to mesonet,ldm;
grant select on products_1999_0106 to nobody,apache;

-- ________________________________________________________________
create table products_1999_0712(
  CONSTRAINT __products19990712_check
  CHECK(entered >= '1999-07-01 00:00+00'::timestamptz
        and entered < '2000-01-01 00:00+00'))
  INHERITS (products);

CREATE INDEX products_1999_0712_pil_idx on products_1999_0712(pil);
CREATE INDEX products_1999_0712_entered_idx on products_1999_0712(entered);
CREATE INDEX products_1999_0712_source_idx on products_1999_0712(source);
create index products_1999_0712_pe_idx on products_1999_0712(pil, entered);
GRANT all on products_1999_0712 to mesonet,ldm;
grant select on products_1999_0712 to nobody,apache;
