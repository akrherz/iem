-- We cleaned up the database and can enforce some constraints now, whew

alter table warnings alter issue set not null;
alter table warnings alter expire set not null;
alter table warnings alter updated set not null;
alter table warnings alter product_issue set not null;
alter table warnings alter init_expire set not null;
