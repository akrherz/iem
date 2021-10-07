# Run in a loop, please
while true; do
    python ingest_isusm.py; mailx -s 'ISUSM Ingest Restarted' akrherz@iastate.edu
    sleep 60
done
