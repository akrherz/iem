<html>

<head>
    <style type="text/css">
        p {
            width: 800px;
            text-indent: 2em;
        }

        body {
            margin-left: 5px;
            border-left-width: 3px;
            border-color: blue;
            background-color: #eeeeee;
        }
    </style>
</head>

<body>

    <h3>NWS Text Product Finder</h3>

    <p>This is a legacy interface that will be kept around as long as folks continue
        to use it. More modern interfaces exist with the <a href="list.phtml">list by source/date</a>
        and <a href="/wx/afos/">list by pil</a> interfaces.</p>

    <p>Using our local <a href="http://www.unidata.ucar.edu/projects/idd/index.html">Unidata IDD</a>
        data feed, a simple script archives NWS text products into a database.
        The above form allows you to query this database for recent products. You must know
        the <a href="http://www.nws.noaa.gov/datamgmt/x_ref/xr04_X_ref_by_NNN.xlsx">AFOS PIL</a> in order to
        get the products you want.</p>

    <ul>
        <li><a href="http://www.nws.noaa.gov/datamgmt/x_ref/xr04_X_ref_by_NNN.xlsx">NNN Categories</a></li>
    </ul>


    <div style="margin: 5px; padding: 5px; border: 1px dashed; background: #eeeeee;">
        <b>Aliases</b>
        <pre>
WARxxx    Retrieve union of Tornado (TOR), Severe T'storm (SVR)
          Flash Flood Warning (FFW), Severe Weather Statement (SVS)
          and Local Storm Report (LSR)

</pre>
        <b>MOS PILS</b>
        <pre>
PIL       Description             Product ID for Des Moines
ECMxxx    ECMWF Guidance M         ECMDSM
ECSxxx    ECMWF Guidance S         ECSDSM
ECXxxx    ECMWF Guidance X         ECXDSM
MAVxxx    GFS MOS Guidance         MAVDSM
METxxx    NAM MOS Guidance         METDSM
MEXxxx    GFSX MOS Guidance        MEXDSM
NBExxx    National Blend E         NBEDSM
NBHxxx    National Blend H         NBHDSM
NBPxxx    National Blend P         NBPDSM
NBSxxx    National Blend S         NBSDSM
NBXxxx    National Blend X         NBXDSM

And model output

FRHxx     Eta Output               FRH68
FRHTxx    NGM Output               FRHT68
</pre>

        <b>Other Favorites:</b>
        <pre>
REPNT2  NHC Vortex Message
PMDHMD  Model Diagnostic Discussion
PMDSPD  Short Range Prognostic Discussion
PMDEPD  Extended Forecast Discussion
SWOMCD  SPC Mesoscale Discussion
SWODY1  SPC Day 1
SWODY2  SPC Day 2
AFDDMX  Des Moines WFO Area Forecast Discussion
SELX    Convective Watch where "X" is a number between 0-9
</pre>
    </div>

</body>

</html>