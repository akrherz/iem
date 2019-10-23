# https://travis-ci.community/t/install-postgresql-11/3894/5
sudo service postgresql stop
sudo apt-get --yes remove postgresql-10-postgis-2.4
sudo apt install -yq --no-install-suggests --no-install-recommends postgresql-11-postgis-2.5-scripts postgresql-11 postgresql-client-11 postgresql-11-postgis-2.5
sed -e 's/^port.*/port = 5432/' /etc/postgresql/11/main/postgresql.conf > postgresql.conf
sudo chown postgres postgresql.conf
sudo mv postgresql.conf /etc/postgresql/11/main
sudo cp /etc/postgresql/10/main/pg_hba.conf /etc/postgresql/11/main/pg_hba.conf
sudo service postgresql restart 11
