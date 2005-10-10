<html>
<head>
<?php
  include("../../config/settings.inc.php");
  $station = isset($_GET['station']) ? $_GET["station"]: "SSAS2";
  $min = isset($_GET["min"]) ? $_GET["min"] : 1;
  include("$rootpath/include/keloLoc.php");
  include("$rootpath/include/imagemaps.php");
 if (strlen($min) == 0){
   $secs = 600;
   $min = 1;
 }
 $secs = intval($min) * 60;
?>
  <title>IEM | KELO WeatherNet | <?php echo $Scities[$station]["short"]; ?></title>
  <meta http-equiv="refresh" content="<?php echo $secs; ?>; URL=kelo_fe.php?min=<?php echo $min; ?>&station=<?php echo $station; ?>">

</head>
<body bgcolor="#96aae7">

<center>
<form method="POST" action="kelo_fe.php" name="st">
<?php
 
  echo "SchoolNet Site: ";
echo "<select  onChange=\"location=this.form.station.options[this.form.station.selectedIndex].value\" name=\"station\">\n";

for ($i = 0; $i < count($Scities); $i++) {
  $city = current($Scities);
  echo "<option value=\"/content/kelo_fe.php?min=".$min."&station=". $city["id"] ."\"";
  if ($station == $city["id"]){
        echo " SELECTED ";
  }
  echo " >". $city["city"] ."\n";
  next($Scities);
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
