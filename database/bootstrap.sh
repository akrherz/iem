# setup databases

psql -c 'create user nobody;' -U postgres
psql -c 'create user apache;' -U postgres
psql -c 'create user mesonet;' -U postgres
psql -c 'create user apiuser;' -U postgres

for db in afos mesosite postgis snet \
asos  hads      mos        rwis     squaw \
awos iem       other      scan     wepp \
coop isuag      portfolio  smos
do
 psql -c "create database $db;" -U postgres
 psql -f init/${db}.sql -U postgres -q $db
psql -f init/functions.sql -U postgres -q $db
done


