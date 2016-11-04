<?php 
include("../../config/settings.inc.php");
include("../../include/myview.php");
$t = new MyView();
define("IEM_APPID", 20);
$t->thispage = "archive-schema";
$t->title = "Archived Data Schema";

$url = sprintf("https://mesonet.agron.iastate.edu/archive/data/%s", gmdate('Y/m/d'));
$u = sprintf("<a href=\"%s\">%s</a>\n", $url, $url);
$d = 

$t->content = <<<EOF

<h3>Archived Data Schema</h3>

<p>The IEM stores
most of its archive in a web accessible directory tree structure.  Here is
the storage schema for today's data:</p>
<pre>
ROOT={$u}
|- base folder full of various images for the date 
|- GIS
   |- NWS coop obs shapefile and road conditions shapefile per update
   |- kcci
      |- KCCI LiveSuper DopplerHD radar imagery
   |- sat
      |- GOES Conus Satellite imagery TIF
   |- uscomp
      |- CONUS NEXRAD base reflectivity ~1km
|- bufkit
   |- BUFKIT files for various model runs for many sites in/near Iowa
|- camera
   |- Per webcam site 5minute imagery
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

EOF;
$t->render('single.phtml');
?>
