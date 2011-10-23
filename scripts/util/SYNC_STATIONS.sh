#!/bin/sh
# Need to sync all our station metadata, when we add new sites!

python checkElevation.py
python assignCounty.py
python assignClimate.py
python checkWFO.py
python set_timezone.py
