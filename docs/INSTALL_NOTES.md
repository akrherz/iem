# Point php.ini at memcache for sessions
[Session]
session.save_handler = memcache
session.save_path = "tcp://iem-memcached:11211"
