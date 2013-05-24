<?php 
/*
 * Attempt to actually document the RASTERs the IEM produces and stores
 * within its archives
 */
include("../../config/settings.inc.php");
require_once(ROOTPATH ."/include/database.inc.php");
$mesosite = iemdb("mesosite");

$TITLE = "IEM GIS RASTER Documentation";
require_once(ROOTPATH ."/include/header.php");
?>

<h3>IEM GIS RASTER Documentation</h3>

<p>The IEM produces a number of RASTER images meant for GIS use. These RASTERs
are typically provided on the IEM website as 8 bit PNG images.  This means there
are 256 slots available for a binned value to be placed.  This page attempts to
document these RASTER images and provide the lookup table of PNG index to an 
actual value.

<p><table cellspacing="0" cellpadding="3" border="1">
<thead><tr><th>Code</th><th>Description</th><th>Units</th></tr></thead>
<tbody>
<?php
$rs = pg_query($mesosite, "SELECT * from raster_metadata
  ORDER by name ASC");

for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
  echo sprintf("<tr><th>%s</th><td>%s</td><td>%s</td></tr>\n", $row["name"],
  		$row["description"], $row["units"]);

}

?>
</tbody>
</table>


<?php 
require_once(ROOTPATH ."/include/footer.php");
?>