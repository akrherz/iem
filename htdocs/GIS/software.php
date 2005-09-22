<?php 
include("../../config/settings.inc.php");
$page = "gis";
$TITLE = "IEM | ASOS Data";
include("$rootpath/include/header.php"); ?>

<TR><TD>
<b>Nav:</b> <a href="/GIS/">GIS</a> <b> > </b> Software

<h3 class="heading">GIS Software</h3>

<div class="text">
<p>The GIS apps on the IEM are not generated from some
blackbox.  There are real scripts and programs that drive the apps and 
dynamic plots.  Here is a listing of software that you may find useful.</p>

<table width="100%">

<tr class="even">
  <td colspan=4>University of Minnesota MapServer</td></tr>
  <tr>
   <td>Homepage:</td><td><a href="http://mapserver.gis.umn.edu/">http://mapserver.gis.umn.edu/</a></td></tr>
   <tr><td>Version / Date:</td><td>3.6.1 <br> 1 Aug 2002</td></tr>
  <tr>
   <td colspan="2">
     From their website, "MapServer is an  OpenSource  development environment for building spatially enabled Internet applications. The software builds upon other popular OpenSource or freeware systems like Shapelib, FreeType, Proj.4, libTIFF, Perl  and others. MapServer will run where most commercial systems won't or can't, on Linux/Apache platforms. MapServer is known to compile on most UNIXes and will run under Windows NT/98/95."
   </td></tr>

<tr class="even">
  <td colspan=2>PostGIS</td></tr>
  <tr>
   <td>Homepage:</td><td><a href="http://postgis.refractions.net">http://postgis.refractions.net</a></td></tr>
   <tr><td>Version / Date:</td><td>0.7 <br> 1 Aug 2002</td></tr>
  <tr>
    <td colspan=2>
     PostGIS is a spatial extension to the PostgreSQL database system.</td>
  </tr>

<tr class="even">
  <td colspan=2>PHP Mapscript</td></tr>
  <tr>
    <td>Homepage:</td><td><a href="http://www2.dmsolutions.ca/webtools/php_mapscript/index.html">http://www2.dmsolutions.ca/webtools/php_mapscript/index.html</a></td></tr>
  <tr>
   <td>Version / Date:</td><td>(packaged with MapServer)</td></tr>
  <tr>
   <td colspan=2>
    PHP MapScript module provides access to MapServer MapScript functions 
    and classes from PHP scripts.  The power of PHP scripting is thus combined
    with the plotting power of MapServer.</td></tr>

<tr class="even">
  <td colspan=2>Python Shapelib</td></tr>
  <tr>
   <td>Homepage:</td><td><a href="ftp://intevation.de/users/bh/pyshapelib-0.2.tar.gz">ftp://intevation.de/users/bh/pyshapelib-0.2.tar.gz</a></td></tr>
  <tr>
   <td>Version / Date:</td><td>0.2 <br> 15 Jun 2001</td></tr>
   <td colspan=2>
     PyShapelib provides python bindings to shapelib.  Shapelib is a library
    for manipulating shapefiles.  Thus you can edit shapefiles from Python.
   </td></tr>

</table></div>

<?php include("$rootpath/include/footer.php"); ?>
