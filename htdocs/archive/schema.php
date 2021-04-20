<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
define("IEM_APPID", 20);
$t->title = "Archived Data Schema";

$url = sprintf("https://mesonet.agron.iastate.edu/archive/data/%s", gmdate('Y/m/d'));
$u = sprintf("<a href=\"%s\">%s</a>\n", $url, $url);

$url2 = sprintf("https://mtarchive.geol.iastate.edu/%s", gmdate('Y/m/d'));
$u2 = sprintf("<a href=\"%s\">%s</a>\n", $url2, $url2);


$t->content = <<<EOF

<h3>Archived Data Schema</h3>

<p>The IEM maintains two directly web-accessible trees of archived weather
products.  This page provides a crude schema of what products are archived and
where within the directory tree you can find them.  The reason there are
two archives is that the products have different funding / support resources
and legacy.</p>

<p>The products are generally organized by UTC date, but some of the products
found are for the local/Iowa calendar date.</p>

<pre>
ROOT={$u}
|- base folder full of various images for the date 
|- GIS
   |- NWS coop obs shapefile and road conditions shapefile per update
   |- kcci
      |- KCCI LiveSuper DopplerHD radar imagery
   |- sat
      |- GOES Conus Satellite imagery TIF
   |- {akcomp,hicomp,prcomp,uscomp}
      |- NEXRAD composites
   | - hrrr reflectivity imagery
   | - mrms imagery
   | - ifc Iowa Flood Center precipitation imagery
   | - ridge single site NEXRAD RADAR imagery 
|- camera
   |- Per webcam site 5 minute interval imagery
|- comprad
   |- Iowa pre-generated NEXRAD imagery w/ warnings and watches
|- hunrad
   |- Pre-generated NEXRAD imagery w/ warnings and watches Alabama
|- ictrad
   |- Pre-generated NEXRAD imagery w/ warnings and watches Kansas
|- lotrad
   |- Pre-generated NEXRAD imagery w/ warnings and watches Illinois
|- raw
   |- Raw datafiles for the AWOS and RWIS network
|- srad
   |- Pre-generated NEXRAD imagery w/ warnings and watches South Dakota
|- sel[0-10]rad
   |- Pre-generated NEXRAD imagery w/ warnings and watches for floating
      watch sectors issued by the Storm Prediction Center
|- text
   |- raw Iowa State road condition reports
   |- noaaport
      |- Saved raw text products from our NWS NOAAPort feed
   |- ot
      |- raw datafiles for some of the sites in the Other Network
|- usrad
   |- Pre-generated NEXRAD imagery w/ warnings and watches United States
|- stage4
   |- Archive of the NCEP Stage4 Precipitation product in Grib format
</pre>

<pre>
ROOT={$u2}
|- base folder full of various images for the date
   | - bufkit :: Archive of BUFKIT data files for a RAP, GFS, NAM, SREF models
   | - cod :: GOES 16+17 Imagery from College of Dupage
   | - gempak :: some NWS/NCEP data in GEMPAK format
   | - grib2 :: limited assortment of NCEP/NWS grib2 products
   | - mrms :: Grib2 NCEP MRMS products
   | - text :: some NWS data in text format
</pre>

EOF;
$t->render('single.phtml');
?>
