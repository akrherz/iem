-- Add index to help situation of WHERE pil = XXX ORDER by entered DESC
set work_mem='64GB';
set maintenance_work_mem='64GB';

create index products_2000_0106_pe_idx on products_2000_0106(pil, entered);
create index products_2000_0712_pe_idx on products_2000_0712(pil, entered);

create index products_2001_0106_pe_idx on products_2001_0106(pil, entered);
create index products_2001_0712_pe_idx on products_2001_0712(pil, entered);

create index products_2002_0106_pe_idx on products_2002_0106(pil, entered);
create index products_2002_0712_pe_idx on products_2002_0712(pil, entered);

create index products_2003_0106_pe_idx on products_2003_0106(pil, entered);
create index products_2003_0712_pe_idx on products_2003_0712(pil, entered);

create index products_2004_0106_pe_idx on products_2004_0106(pil, entered);
create index products_2004_0712_pe_idx on products_2004_0712(pil, entered);

create index products_2005_0106_pe_idx on products_2005_0106(pil, entered);
create index products_2005_0712_pe_idx on products_2005_0712(pil, entered);

create index products_2006_0106_pe_idx on products_2006_0106(pil, entered);
create index products_2006_0712_pe_idx on products_2006_0712(pil, entered);

create index products_2007_0106_pe_idx on products_2007_0106(pil, entered);
create index products_2007_0712_pe_idx on products_2007_0712(pil, entered);

create index products_2008_0106_pe_idx on products_2008_0106(pil, entered);
create index products_2008_0712_pe_idx on products_2008_0712(pil, entered);

create index products_2009_0106_pe_idx on products_2009_0106(pil, entered);
create index products_2009_0712_pe_idx on products_2009_0712(pil, entered);

create index products_2010_0106_pe_idx on products_2010_0106(pil, entered);
create index products_2010_0712_pe_idx on products_2010_0712(pil, entered);

create index products_2011_0106_pe_idx on products_2011_0106(pil, entered);
create index products_2011_0712_pe_idx on products_2011_0712(pil, entered);

create index products_2012_0106_pe_idx on products_2012_0106(pil, entered);
create index products_2012_0712_pe_idx on products_2012_0712(pil, entered);

create index products_2013_0106_pe_idx on products_2013_0106(pil, entered);
create index products_2013_0712_pe_idx on products_2013_0712(pil, entered);

create index products_2014_0106_pe_idx on products_2014_0106(pil, entered);
create index products_2014_0712_pe_idx on products_2014_0712(pil, entered);

create index products_2015_0106_pe_idx on products_2015_0106(pil, entered);
create index products_2015_0712_pe_idx on products_2015_0712(pil, entered);

create index products_2016_0106_pe_idx on products_2016_0106(pil, entered);
create index products_2016_0712_pe_idx on products_2016_0712(pil, entered);
