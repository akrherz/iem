<html>
<head>
<?php
  include("../../config/settings.inc.php");
  $station = isset($_GET['station']) ? $_GET["station"]: "SSAS2";
  $min = isset($_GET["min"]) ? $_GET["min"] : 1;
  include("$rootpath/include/network.php");
$nt = new NetworkTable("KELO");
$cities = $nt->table;
  include("$rootpath/include/imagemaps.php");
 if (strlen($min) == 0){
   $secs = 600;
   $min = 1;
 }
 $secs = intval($min) * 60;
?>
  <title>IEM | KELO WeatherNet | <?php echo $cities[$station]["name"]; ?></title>
  <meta http-equiv="refresh" content="<?php echo $secs; ?>; URL=kelo_fe.php?min=<?php echo $min; ?>&station=<?php echo $station; ?>">

</head>
<body bgcolor="#96aae7">

<center>
<form method="POST" action="kelo_fe.php" name="st">
<?php
 
  echo "WeatherNet Site: ";
echo "<select  onChange=\"location=this.form.station.options[this.form.station.selectedIndex].value\" name=\"station\">\n";

while( list($key, $val) = each($cities) ){
  echo "<option value=\"$rooturl/content/kelo_fe.php?min=".$min."&station=". $key ."\"";
  if ($station == $key){
        echo " SELECTED ";
  }
  echo " >". $val["name"] ."\n";
}


echo "</select>\n";

?>
</form>
<p>
<?php
  echo "<img src=\"kelo.php?station=".$station ."\">\n";
?>

<?php if (! isset($mode) ){ ?>
<br>Refresh Every: 
<form name="refresh" action="kelo_fe.php">
<?php
  $mins = Array(1, 5, 10, 20);
  while (list($key, $val) = each($mins) ){
    echo "<input type=\"radio\" name=\"min\" value=\"". $val ."\" ";
    if ($min == $val){
      echo "CHECKED";
    }
    echo "> ". $val ." min";
  }
?>
<input type="hidden" value="<?php echo $station; ?>" name="station">
<input type="submit" value="Refresh">
</form>
<?php } ?>

</center>

</html>
