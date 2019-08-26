# setup databases
# we want this script to exit 2 so that travis will report any failures

/usr/bin/psql -c 'create user nobody;' -h localhost -U postgres
/usr/bin/psql -c 'create user apache;' -h localhost -U postgres
/usr/bin/psql -c 'create user mesonet;' -h localhost -U postgres
/usr/bin/psql -c 'create user ldm;' -h localhost -U postgres
/usr/bin/psql -c 'create user apiuser;' -h localhost -U postgres

for db in afos mesosite postgis snet \
asos hads  mos        rwis     squaw \
awos iem   other      scan     wepp \
coop isuag portfolio  smos     iemre radar
do
/usr/bin/psql -v "ON_ERROR_STOP=1" -c "create database $db;" -h localhost -U postgres || exit 2
/usr/bin/psql -v "ON_ERROR_STOP=1" -f init/${db}.sql -h localhost -U postgres -q $db || exit 2
/usr/bin/psql -v "ON_ERROR_STOP=1" -f functions.sql -h localhost -U postgres -q $db || exit 2
done

# one offs
/usr/bin/psql -v "ON_ERROR_STOP=1" -c "create database talltowers;" -h localhost -U postgres || exit 2
/usr/bin/psql -v "ON_ERROR_STOP=1" -f init_travis/talltowers.sql -h localhost -U postgres -q talltowers || exit 2
