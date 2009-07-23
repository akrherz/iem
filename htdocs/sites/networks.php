<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$pgconn = iemdb("mesosite");
$rs = pg_prepare($pgconn, "SELECT", "SELECT * from stations 
            WHERE online = 'y' and 
			network = $1 ORDER by name");
include("$rootpath/include/imagemaps.php");

$network = isset($_GET['network']) ? $_GET['network'] : 'IA_ASOS';
$format = isset($_GET['format']) ? $_GET['format'] : 'html';
$nohtml = isset($_GET['nohtml']);

if ($nohtml) header("Content-type: text/plain"); 

if (! $nohtml) {
$TITLE = "IEM Station Locations";
$THISPAGE = "iem-networks";
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
  <td><?php echo selectNetwork($network); ?>
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
		$result = pg_execute($pgconn, "SELECT", Array($network) );
		if ($format == "html"){
		echo "<p><table cellspacing='0' cellpadding='2' border='1'>\n";
		echo "<caption><b>". $network ." Network</b></caption>\n";
		echo "<thead><tr><th>ID</th><th>Station Name</td><th>Latitude<sup>1</sup></th>
			<th>Longitude<sup>1</sup></th><th>Elevation [m]</th></tr></thead>\n";
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
	}

if (! $nohtml) {
?>


<p><h3 class="subtitle">Notes</h3><br>
<b>1</b>:  Latitude and Longitude values are in decimal degrees.
<br />Elevation is expressed in meters above sea level.

<br><br></div>

<!-- Begin the bottom of the page-->

<?php include("$rootpath/include/footer.php"); ?>
<?php } ?>
