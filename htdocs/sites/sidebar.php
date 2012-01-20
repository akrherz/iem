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
	"tables" => Array("name" => "Network Table", "uri" => "networks.php?"),
  "neighbors" => Array("name" => "Neighbors", "uri" => "neighbors.php?"),
  "7dayhilo" => Array("name" => "7 Day High/Low Plot", "uri" => "plot.php?prod=0&"),
  "monthhilo" => Array("name" => "Month High/Low Plot", "uri" => "plot.php?prod=1&"),
  "monthrain" => Array("name" => "Month Rainfall Plot", "uri" => "plot.php?prod=2&"),
  "obhistory" => Array("name" => "Observation History", "uri" => "obhistory.php?",
	"azos" => True),
  "windrose" => Array("name" => "Wind Roses", "uri" => "windrose.phtml?"),
  "custom_windrose" => Array("name" => "Custom Wind Roses", "uri" => "dyn_windrose.phtml?"),
  "calendar" => Array("name" => "Data Calendar", "uri" => "hist.phtml?"),
);

while (list($key,$val) = each($o))
{
	if (array_key_exists("azos", $val) &&  preg_match('/ASOS|AWOS/', $network) <= 0){
		continue;
	}
  	$uri = sprintf("%sstation=%s&network=%s", $val["uri"], $station, $network);
  	echo "<div style=\"";
  	if ($current == $key) echo "background: #eaf;";
  	echo "width: 150px; float: left; padding-left: 10px;\"><a href=\"$uri\">". $val["name"] ."</a></div>";
}

if (preg_match('/ASOS|AWOS/', $network) > 0){
	$uri = sprintf("%s/request/download.phtml?network=%s", $rooturl, $network);
	echo "<div style=\"width: 150px; float: left; padding-left: 10px; border-left: 4px solid #0F0;\"><a href=\"$uri\">Download</a></div>";
}elseif (preg_match('/DCP/', $network) > 0){
	$uri = sprintf("%s/request/dcp/fe.phtml?network=%s", $rooturl, $network);
	echo "<div style=\"width: 150px; float: left; padding-left: 10px; border-left: 4px solid #0F0;\"><a href=\"$uri\">Download</a></div>";
	
}
?>
<br clear="all" />
<form method="GET" name="automatic">
<?php 
if (isset($savevars)){
	while (list($k,$v)=each($savevars)){
		echo sprintf("<input type=\"hidden\" value=\"%s\" name=\"%s\" />",
		$v, $k);
	}
}
?>
<input type="hidden" name="network" value="<?php echo $network; ?>">
<p>Other Sites in network:
<?php 
include_once("$rootpath/include/imagemaps.php");
echo networkSelectAuto($network, $station); 
?>
 or <a href="locate.php?network=<?php echo $network; ?>">select from map</a>
</form>
</div>
