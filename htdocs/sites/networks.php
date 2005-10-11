<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$network = isset($_GET['network']) ? $_GET['network'] : 'IA_ASOS';
$format = isset($_GET['format']) ? $_GET['format'] : 'html';
$nohtml = isset($_GET['nohtml']);

if ($nohtml) header("Content-type: text/plain"); 

if (! $nohtml) {
$TITLE = "IEM Station Locations";
include("$rootpath/include/header.php"); ?>

<h3 class="heading">Network Location Tables</h3>

<div class="text">
<p>With this form, you can generate a station table for any
of the networks listed below.  If there is a particular format for a station
table that you need, please let use know.</p>

<form method="GET" action="networks.php" name="networkSelect">
<table>
<tr>
  <th>Select Observing Network:</th>
  <td><SELECT name="network" size="1">
  <option value="IA_ASOS" <?php if($network == "IA_ASOS") echo "SELECTED"; ?>>ASOS (Automated Surface Observing System)
  <option value="AWOS" <?php if($network == "AWOS") echo "SELECTED"; ?>>AWOS (Automated Weather Observing System)
  <option value="COOPDB" <?php if($network == "COOPDB") echo "SELECTED"; ?>>Iowa Climate Sites (IEM Tracked)
  <option value="DCP" <?php if($network == "DCP") echo "SELECTED"; ?>>DCP (GEOS Data Collection Platforms)
  <option value="ISUAG" <?php if($network == "ISUAG") echo "SELECTED"; ?>>Iowa State AgClimate
  <option value="KCCI" <?php if($network == "KCCI") echo "SELECTED"; ?>>KCCI SchoolNET8 Stations
  <option value="KELO" <?php if($network == "KELO") echo "SELECTED"; ?>>KELO WeatherNet Stations
  <option value="KIMT" <?php if($network == "KIMT") echo "SELECTED"; ?>>KIMT StormNet Stations
  <option value="IA_COOP" <?php if($network == "IA_COOP") echo "SELECTED"; ?>>NWS COOP Observers
  <option value="IA_RWIS" <?php if($network == "IA_RWIS") echo "SELECTED"; ?>>Iowa RWIS (Roadway Weather Information System)
  <option value="KS_RWIS" <?php if($network == "KS_RWIS") echo "SELECTED"; ?>>Kansas RWIS (Roadway Weather Information System)
  <option value="MN_RWIS" <?php if($network == "MN_RWIS") echo "SELECTED"; ?>>Minnesota RWIS (Roadway Weather Information System)
  <option value="WI_RWIS" <?php if($network == "WI_RWIS") echo "SELECTED"; ?>>Wisconsin RWIS (Roadway Weather Information System)
  <option value="MN_ASOS" <?php if($network == "MN_ASOS") echo "SELECTED"; ?>>Minnesota ASOS/AWOS
  <option value="WI_ASOS" <?php if($network == "WI_ASOS") echo "SELECTED"; ?>>Wisconsin ASOS/AWOS
  <option value="IL_ASOS" <?php if($network == "IL_ASOS") echo "SELECTED"; ?>>Illinios ASOS/AWOS
  <option value="MO_ASOS" <?php if($network == "MO_ASOS") echo "SELECTED"; ?>>Missouri ASOS/AWOS
  <option value="KS_ASOS" <?php if($network == "KS_ASOS") echo "SELECTED"; ?>>Kansas ASOS/AWOS
  <option value="NE_ASOS" <?php if($network == "NE_ASOS") echo "SELECTED"; ?>>Nebraska ASOS/AWOS
  <option value="SD_ASOS" <?php if($network == "SD_ASOS") echo "SELECTED"; ?>>South Dakota ASOS/AWOS
  <option value="ND_ASOS" <?php if($network == "ND_ASOS") echo "SELECTED"; ?>>North Dakota ASOS/AWOS
 </SELECT>
  </td>
</tr>
<tr>
  <th>Select Format:</th>
<td>
<select name="format">
  <option value="html" <?php if($format == "html") echo "SELECTED"; ?>>HTML Table
  <option value="csv" <?php if($format == "csv") echo "SELECTED"; ?>>Comma Delimited
  <option value="shapefile" <?php if($format == "shapefile") echo "SELECTED"; ?>>ESRI Shapefile
  <option value="gempak" <?php if($format == "gempak") echo "SELECTED"; ?>>GEMPAK station file
  <option value="awips" <?php if($format == "awips") echo "SELECTED"; ?>>AWIPS station file
  <option value="madis" <?php if($format == "madis") echo "SELECTED"; ?>>MADIS station file
</select>
</td></tr>

<tr>
 <td colspan="2"><input type="checkbox" name="nohtml">Just Table, no HTML</td></tr>

<tr><td colspan="2">
<input type="submit" value="Create Table">
</form>
</td></tr>
</table>

<?php

}

	if (strlen($network) > 0){
		$connection = iemdb("mesosite");
		$query = "SELECT * from stations WHERE online = 'y' and 
			network = '". $network ."' ORDER by name ";
		$result = pg_exec($connection, $query);
		if ($format == "html"){
		echo "<p><table>\n";
		echo "<caption><b>". $network ." Network</b></caption>\n";
		echo "<tr><th>ID</th><th>Station Name</td><th>Latitude<sup>1</sup></th>
			<th>Longitude<sup>1</sup></th><th>Elevation [m]</th></tr>\n";
		for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
			echo "<tr>\n
			  <td>". $row["id"] ."</td>\n
			  <td>". $row["name"] ."</td>\n
			  <td>". round($row["latitude"],5) . "</td>\n
			  <td>". round($row["longitude"],5) . "</td>\n
			  <td>". $row["elevation"]. "</td>\n
			  </tr>";
		}
		echo "</table>\n";

		} else if ($format == "csv") {
		   if (! $nohtml) echo "<p><b>". $network ." Network</b></p>\n";
		   if (! $nohtml) echo "<pre>\n";
		  echo "stid,station_name,lat,lon,elev\n";
		  for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
                        echo $row["id"] .","
                          . $row["name"] .","
                          . round($row["latitude"],5). ","
                          . round($row["longitude"],5). ","
                          . $row["elevation"]. "\n";
                  }
		  if (! $nohtml)  echo "</pre>\n";
		}
  else if ($format == "shapefile") {
    dl($mapscript);
    /* Create SHP,DBF bases */
    $filePre = "${network}_locs";
    $shpFname = "/var/www/htdocs/tmp/$filePre";
    @unlink($shpFname.".shp");
    @unlink($shpFname.".shx");
    @unlink($shpFname.".dbf");
    @unlink($shpFname.".zip");
    $shpFile = ms_newShapeFileObj($shpFname, MS_SHP_POINT);
    $dbfFile = dbase_create( $shpFname.".dbf", array(
      array("ID", "C", 6),
      array("NAME", "C", 50),
      array("NETWORK","C",10),
     ));

    for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
      $shp = ms_newShapeObj(MS_SHAPE_POINT);
      $pt = ms_newPointobj();
      $pt->setXY( $row["longitude"], $row["latitude"], 0);
      $line = ms_newLineObj();
      $line->add( $pt );
      $shp->add($line);
      $shpFile->addShape($shp);
      dbase_add_record($dbfFile, array(
         $row["id"],
         $row["name"],
         $row["network"],
      ));
    }   

    $shpFile->free();
    dbase_close($dbfFile);
    chdir("/var/www/htdocs/tmp/");
    copy("/mesonet/data/gis/meta/4326.prj", $filePre.".prj");
    popen("zip ".$filePre.".zip ".$filePre.".shp ".$filePre.".shx ".$filePre.".dbf ".$filePre.".prj", 'r');
    echo "Shapefile Generation Complete.<br>";
    echo "Please download this <a href=\"/tmp/".$filePre.".zip\">zipfile</a>.";
  }
       else if ($format == "awips") {
         if (! $nohtml) echo "<pre>\n";
         for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
           printf("%s|%s|%-30s|%4.1f|%2.5f|%3.5f|GMT|||1||||\n", $row["id"], $row["id"], $row["name"], $row["elevation"], $row["latitude"], $row["longitude"]);
         } // End of for
          if (! $nohtml) echo "</pre>\n";
        }

  else if ($format == "madis") {
         if (! $nohtml) echo "<pre>\n";

         for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
         if (substr($row["network"],0,4) == "KCCI") $row["network"] = "KCCI-TV";
         if (substr($row["network"],0,4) == "KELO") $row["network"] = "KELO-TV";
         if (substr($row["network"],0,4) == "KIMT") $row["network"] = "KIMT-TV";
           printf("%s|%s|%-39s%-11s|%4.1f|%2.5f|%3.5f|GMT|||1||||\n", $row["id"], $row["id"], $row["name"], $row["network"], $row["elevation"], $row["latitude"], $row["longitude"]);
         } // End of for
          if (! $nohtml) echo "</pre>\n";
  }

  else if ($format == "gempak") {
		  if (! $nohtml) echo "<pre>\n";
		  for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
                        echo str_pad($row["id"], 9)
			  .  str_pad($row["synop"], 7)
                          .  str_pad($row["name"], 33)
			  .  str_pad($row["state"], 3)
			  .  str_pad($row["country"], 2) 
                          .  sprintf("%6.0f", $row["latitude"] * 100)
                          .  sprintf("%7.0f", $row["longitude"] * 100) 
			  .  sprintf("%6.0f", $row["elevation"])
			  . "\n";
                  }
		  if (! $nohtml) echo "</pre>\n";
		}
		pg_close($connection);
	}

if (! $nohtml) {
?>


<p><h3 class="subtitle">Notes</h3><br>
<b>1</b>:  Latitude and Longitude values are in decimal degrees.

<br><br></div>

<!-- Begin the bottom of the page-->

<?php include("$rootpath/include/footer.php"); ?>
<?php } ?>
