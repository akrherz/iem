-- Storage of SPS issue and expire times
ALTER TABLE text_products add issue timestamptz;
ALTER TABLE text_products add expire timestamptz;

CREATE INDEX text_products_issue_idx on text_products(issue);
CREATE INDEX text_products_expire_idx on text_products(expire);

GRANT SELECT on text_products to nobody,apache;