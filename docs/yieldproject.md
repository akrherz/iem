FACTs Project Meeting Notes
========

26 Jun 2019 Archontoulis Angelos
----

- For next year, the PSIMs domain may expand to MN and NE
- [ ] akrherz/iem#199 can we move IEMRE to the database to make it faster
- [ ] would like to launch a crop dry down app by Aug 3
- Instead of providing average RH, I could just provide daily min/max
- [ ] produce a map showing RH computation bias by averaging method
- [ ] NASA POWER has a RH field I could potentially use
- [ ] daymet allow maybe has a RH field I could use

23 May 2019 Archontoulis Isaiah
----

- [ ] CFS may have some strange issues around cold days < 40F
- [x] Send Angelo new map addresses
- [x] Take location labels off the map
- [x] Plot Magnitude of GDD departure

2 May 2019 Archontoulis
----

- [ ] he wants CFS radiation capped at 31 MJ/d
- Plan is to push weekly update at 9 AM Wednesday, so runs made on Tuesday
- [ ] Deliver a WPC Map of forecasted 7 day precipitation
- [x] GDD departures over the coming week
- [x] next week daily max temperature and daily min temperature
- [ ] create a pyIEM zoom for the corn belt, IA->IN
- [ ] PSIMs yearly scenario substitions, like what is done for station data

5 Apr 2019 Archontoulis, Angelos, Isaiah, one other
----

- The regional interest this year is IA, IL and IN
- [ ] investigate NASA Power and see how difference its radiation is
- There are three deliverables they want
- [x] Static 1980-2018 PSIMs files, like I generated last year
- [x] four routinely updated PSIMs files, one for each CFS 9 mon realization
- [ ] scenarios with all years substituted.  This may be too much data for
    them, so lower priority for now.

5 Jan 2017 Dr Archontoulis
----

- Review Nov 1 to today plot, to ensure it is doing the right thing
- [ ] remove the march 15 to today plot, not used
- [ ] Add NASS county yield somehow to the aridity x/y plot
- A new folder was created at dropbox for the uploads to go to

11 Apr 2016 Dr Archontoulis
----

- He now has 6 files processed up until 23 March, wants data till 30 Nov
- March 15th start date for the various GDD, etc plots
- For the future scatter, just make it a cloud with some lines in it
- Would like to use dropbox for sharing files
- Add a GDD column and others for the APSIM met file
- FIX: the units of the soil moisture shown in the download page
- Will want me to produce a differently formatted file later in July
- He wants 4 days of forecast data
- Output file name is Ames_YYYYmmdd.met

24 Mar 2016 Dr Archontoulis
----

- Discuss my involvement with the yield forecasting project
- Dr Helmers Cobbs site will be sending hourly precip data my way
- They have a good web developer, so I am just wrangling data
- I need to look at a dataset called agmerra
- So the complicated routine about producing a 1980-2015 weather data file
that has this year's data + forecast replacing that year's period.  Then the
rest of the year is simply taking that old year's data.  I'll automate this
- Look into usage of GFS + CFS for forecast data
- There are six sites in play
