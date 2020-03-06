---
--- Store 404s for downstream analysis
CREATE TABLE weblog(
    valid timestamptz DEFAULT now(),
    client_addr inet,
    uri text,
    referer text,
    http_status int
);
ALTER TABLE weblog OWNER to mesonet;
GRANT ALL on weblog to nobody,apache;
