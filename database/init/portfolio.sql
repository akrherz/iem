-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (-1, now());

-- Portfolio database

--
-- Base of IEM Trouble tickets
--
CREATE TABLE tt_base(
  id SERIAL UNIQUE NOT NULL,
  portfolio varchar(30),
  s_mid varchar(10),
  entered timestamptz DEFAULT now(),
  last timestamptz DEFAULT now(),
  closed timestamptz,
  subject varchar(256),
  status varchar(30),
  author varchar(30),
  sensor varchar);
CREATE INDEX tt_base_s_mid_idx on tt_base(s_mid);
GRANT SELECT on tt_base to nobody,apache;

--
-- IEM Trouble Ticket Log
--
CREATE TABLE tt_log(
  id SERIAL UNIQUE NOT NULL,
  portfolio varchar(30),
  s_mid varchar(10),
  entered timestamptz DEFAULT now(),
  author varchar(30),
  status_c varchar(30),
  comments text,
  tt_id int REFERENCES tt_base(id));
CREATE INDEX tt_log_tt_idx on tt_log(tt_id);
GRANT SELECT on tt_log to nobody,apache;

--
-- IEM Site Contacts
--
CREATE TABLE iem_site_contacts(
  id SERIAL NOT NULL,
  portfolio varchar(30),
  s_mid varchar(10),
  name varchar(256),
  phone varchar(20),
  email varchar(100));
