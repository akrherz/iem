# setup databases
# we want this script to exit 2 so that travis will report any failures

psql -c 'create user nobody;' -U postgres
psql -c 'create user apache;' -U postgres
psql -c 'create user mesonet;' -U postgres
psql -c 'create user ldm;' -U postgres
psql -c 'create user apiuser;' -U postgres

for db in afos mesosite postgis snet \
asos hads  mos        rwis     squaw \
awos iem   other      scan     wepp \
coop isuag portfolio  smos
do
psql -v "ON_ERROR_STOP=1" -c "create database $db;" -U postgres || exit 2
psql -v "ON_ERROR_STOP=1" -f init/${db}.sql -U postgres -q $db || exit 2
psql -v "ON_ERROR_STOP=1" -f functions.sql -U postgres -q $db || exit 2
done
