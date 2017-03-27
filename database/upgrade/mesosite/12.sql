-- Storage of talltowers analog request queue
CREATE TABLE talltowers_analog_queue
    (stations varchar(32),
    sts timestamptz,
    ets timestamptz,
    fmt varchar(32),
    email varchar(128),
    aff varchar(256),
    filled boolean DEFAULT 'f',
    valid timestamptz DEFAULT now());
GRANT ALL on talltowers_analog_queue to apache, mesonet;
