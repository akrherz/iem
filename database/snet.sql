CREATE TABLE alldata (
    station character varying(5),
    valid timestamp with time zone,
    tmpf smallint,
    dwpf smallint,
    drct smallint,
    sknt real,
    pday real,
    pmonth real,
    srad real,
    relh real,
    alti real,
    gust real
);

CREATE TABLE t2012_05 () INHERITS (alldata);
