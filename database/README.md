# Simple Schema Manager

Eh, I am sure there are much better ways to manage database schema than this,
but alas, here it is.  Fundamentally, we support the following scenarios.

1. A newly setup PostgreSQL database.
2. An upgrade path from previously deployed databases
3. A means to bootstrap a database schema and some initial data to support
Travis-CI testing.

The `init` folder contains the initial schema plus incremental changes that
are also tracked in sequential `upgrade` files.  A recent change was to update
the files in `init` with any schema updates made.  The magic happens with a
dedicated table in each database known as `iem_schema_manager_version`,
which tracks a integer value representing the most recent schema update made.

Simply running:

    python schema_manager.py

and things should take care of themselves.  The `bootstrap.sh` exists for
initial deployments, like on Travis-CI.

### iemdb-hads one-off

Sadly, there is a big hack in here to allow for the `hads` database to exist
on a different PostgreSQL server. This database is over 1TB in size in
production, so it is running on cheaper hardware.  The current iemdb server
is all SSD, so nothing else locally to use :/  If you have the hostname
`iemdb-hads` pointing at your single database server, it should work around
this hack.
