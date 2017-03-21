<?php 
include("../../config/settings.inc.php");
include_once "../../include/myview.php";
$t = new MyView();
$t->title = "GIS Software";
$t->thispage = "gis-software";

$t->content = <<<EOF
<ol class="breadcrumb">
	<li><a href="/GIS">GIS</a></li>
	<li class="active">Software</li>		
</ol>

<h3>GIS Software</h3>

<p>The GIS apps on the IEM are not generated from some
blackbox.  There are real scripts and programs that drive the apps and 
dynamic plots.  Here is a listing of software that you may find useful.</p>

<table class="table">

<tr class="even">
  <td colspan=4>University of Minnesota MapServer</td></tr>
  <tr>
   <td>Homepage:</td><td><a href="http://mapserver.org/">http://mapserver.org/</a></td></tr>
  <tr>
   <td colspan="2">
     From their website, "MapServer is an  OpenSource  development environment for building spatially enabled Internet applications. The software builds upon other popular OpenSource or freeware systems like Shapelib, FreeType, Proj.4, libTIFF, Perl  and others. MapServer will run where most commercial systems won't or can't, on Linux/Apache platforms. MapServer is known to compile on most UNIXes and will run under Windows NT/98/95."
   </td></tr>

<tr class="even">
  <td colspan=2>PostGIS</td></tr>
  <tr>
   <td>Homepage:</td><td><a href="http://postgis.refractions.net">http://postgis.refractions.net</a></td></tr>
  <tr>
    <td colspan=2>
     PostGIS is a spatial extension to the PostgreSQL database system.</td>
  </tr>

<tr class="even">
  <td colspan=2>PHP Mapscript</td></tr>
  <tr>
    <td>Homepage:</td><td><a href="http://www2.dmsolutions.ca/webtools/php_mapscript/index.html">http://www2.dmsolutions.ca/webtools/php_mapscript/index.html</a></td></tr>
  <tr>
   <td colspan=2>
    PHP MapScript module provides access to MapServer MapScript functions 
    and classes from PHP scripts.  The power of PHP scripting is thus combined
    with the plotting power of MapServer.</td></tr>

<tr class="even">
  <td colspan=2>PyShp</td></tr>
  <tr>
   <td>Homepage:</td><td><a href="https://pypi.python.org/pypi/pyshp">https://pypi.python.org/pypi/pyshp</a></td></tr>
  <tr>
   <td colspan=2>
     The Python Shapefile Library (pyshp) provides read and write support for the Esri Shapefile format.
   </td></tr>

</table>
EOF;
$t->render("single.phtml");
?>
