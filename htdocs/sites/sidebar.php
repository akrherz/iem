<div>
<strong><?php echo $metadata["name"]; ?> Links:</strong>
<p>
<?php
$o = Array(
  "base" => Array("name" => "Information", "uri" => "site.php?"),
  "current" => Array("name" => "Last Ob", "uri" => "current.php?"),
  "pics" => Array("name" => "Photographs", "uri" => "pics.php?"),
  "cal" => Array("name" => "Calibration", "uri" => "cal.phtml?"),
  "loc" => Array("name" => "Location Maps", "uri" => "mapping.php?"),
  "meteo" => Array("name" => "Meteogram", "uri" => "meteo.php?"),
  "neighbors" => Array("name" => "Neighbors", "uri" => "neighbors.php?"),
  "7dayhilo" => Array("name" => "7 Day High/Low Plot", "uri" => "plot.php?prod=0&"),
  "monthhilo" => Array("name" => "Month High/Low Plot", "uri" => "plot.php?prod=1&"),
  "monthrain" => Array("name" => "Month Rainfall Plot", "uri" => "plot.php?prod=2&"),
  "windrose" => Array("name" => "Wind Roses", "uri" => "windrose.phtml?"),
  "custom_windrose" => Array("name" => "Custom Wind Roses", "uri" => "dyn_windrose.phtml?"),
  "calendar" => Array("name" => "Data Calendar", "uri" => "hist.phtml?"),
);

while (list($key,$val) = each($o))
{
  $uri = sprintf("%sstation=%s&network=%s", $val["uri"], $station, $network);
  echo "<div style=\"";
  if ($current == $key) echo "-moz-border-radius: 1em; border: 1px solid #c00 ;";
  echo "width: 150px; float: left; padding-left: 10px;\"><a href=\"$uri\">". $val["name"] ."</a></div>";
}
?>
<br clear="all" />
<form method="GET" name="automatic">
<input type="hidden" name="network" value="<?php echo $network; ?>">
<p>Other Sites in network:
<?php 
include_once("$rootpath/include/imagemaps.php");
echo networkSelectAuto($network, $station); 
?>
 or <a href="locate.php?network=<?php echo $network; ?>">select from map</a>
</form>
</div>
