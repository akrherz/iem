<?php
 include("../../../config/settings.inc.php");
 include("$rootpath/include/database.inc.php");

  $ostation = isset($_GET["ostation"]) ? $_GET["ostation"] : "";
  $station = isset($_GET['station']) ? $_GET["station"] : "";
  $mode = isset($_GET["mode"]) ? $_GET["mode"]: "rt";
$syear = isset($_GET["syear"]) ? $_GET["syear"] : date("Y");
$smonth = isset($_GET["smonth"]) ? $_GET["smonth"]: date("m");
$sday = isset($_GET["sday"]) ? $_GET["sday"] : date("d");
$days = isset($_GET["days"]) ? $_GET["days"]: 2;
$subc = isset($_GET["subc"]) ? $_GET["subc"] : "";
$dwpf = isset($_GET["dwpf"]) ? $_GET["dwpf"] : "";
$tmpf = isset($_GET["tmpf"]) ? $_GET["tmpf"] : "";
$s0 = isset($_GET["s0"]) ? $_GET["s0"]: "";
$s1 = isset($_GET["s1"]) ? $_GET["s1"]: "";
$s2 = isset($_GET["s2"]) ? $_GET["s2"]: "";
$s3 = isset($_GET["s3"]) ? $_GET["s3"]: "";

 include("$rootpath/include/selectWidget.php");
 $sw = new selectWidget("$rooturl/plotting/rwis/sf_fe.php", "$rooturl/plotting/rwis/sf_fe.php?", "IA_RWIS");
 $swf = Array("network" => "IA_RWIS", "s0" => 1, "s1" => 1, "s2" => 1, 
              "s3" => 1, "tmpf" => 1, "dwpf" => 1, "subc" => 1);
 $sw->setformvars($swf);
 $sw->logic($_GET);
 $swinterface = $sw->printInterface();

	include("$rootpath/include/header.php"); 
?>
<?php include("$rootpath/include/imagemaps.php"); ?>
<?php include("$rootpath/include/forms.php"); ?>
<b>Nav:</b> <a href="<?php echo $rooturl; ?>/RWIS/">RWIS</a> <b> > </b>
Pavement Temperature Time Series

<br><br>

<form method="GET" action="sf_fe.php" name="menu">
<input type="hidden" name="ostation" value="<?php echo $station; ?>">
<h2 class="heads">Site Selection:</h2>
Select from list: <?php echo networkSelect("IA_RWIS",$station); ?> or 
<a href="sf_fe.php">Select Visually</a>

<?php 
  if (strlen($station) > 0 ) { 
?>
<h2 class="heads">Plot time span:</h2>
<table width="100%">
 <tr>
   <td valign="TOP"><input type="radio" name="mode" value="rt" <?php if ($mode == "rt") echo "CHECKED"; ?>>Current</td>
   <td><input type="radio" name="mode" value="hist" <?php if ($mode == "hist") echo "CHECKED"; ?>>Historical
  <br>Start Year:<?php echo yearSelect2(1995, $syear, "syear"); ?>
  Start Month:<?php echo monthSelect2($smonth, "smonth"); ?>
  Start Day:<?php echo daySelect2($sday, "sday"); ?>
  <br>Number of days:
   <select name="days">
     <option value="1" <?php if ($days == "1") echo "SELECTED"; ?>>1
     <option value="2" <?php if ($days == "2") echo "SELECTED"; ?>>2
     <option value="3" <?php if ($days == "3") echo "SELECTED"; ?>>3
     <option value="4" <?php if ($days == "4") echo "SELECTED"; ?>>4
     <option value="5" <?php if ($days == "5") echo "SELECTED"; ?>>5
   </td>
 </tr>
</table>

<h2 class="heads">Modify Plot:</h2>
<?php

  $c0 = iemdb('rwis');
  $q0 = "SELECT * from sensors WHERE station = '". $station ."' ";
  $r0 = pg_exec($c0, $q0);

  $row = @pg_fetch_array($r0, 0);
  $ns0 = $row['sensor0'];
  $ns1 = $row['sensor1'];
  $ns2 = $row['sensor2'];
  $ns3 = $row['sensor3'];

  pg_close($c0);

  $cgiStr = "&mode=$mode&sday=$sday&smonth=$smonth&syear=$syear&days=$days&";
  echo "<table width=\"100%\">
      <tr><td><b>Restrict Plot:</b>
      <br><input type=\"checkbox\" name=\"limit\" value=\"yes\" ";
  if (isset($_GET["limit"])) echo "CHECKED";
  echo ">Temps between 25-35
    </td><td><b>Pavement Sensors:</b><br>\n";
  if (strlen($ns0) > 0) {
    echo "<input type=\"checkbox\" name=\"s0\" ";
    if (isset($_GET["s0"])) {
      echo "CHECKED";
      $cgiStr .= "&s0=yes";
      }
    echo ">". $ns0 ."\n";
  }
  if (strlen($ns1) > 0) {
    echo "<br><input type=\"checkbox\" name=\"s1\" ";
    if (isset($_GET["s1"])) {
      echo "CHECKED";
      $cgiStr .= "&s1=yes";
    }
    echo ">". $ns1 ."\n";
  }
  if (strlen($ns2) > 0) {
    echo "<br><input type=\"checkbox\" name=\"s2\" ";
    if (isset($_GET["s2"])) {
      echo "CHECKED";
      $cgiStr .= "&s2=yes";
    }
    echo ">". $ns2 ."\n";
  }
  if (strlen($ns3) > 0) {
    echo "<br><input type=\"checkbox\" name=\"s3\" ";
    if (isset($_GET["s3"])) {
      echo "CHECKED";
      $cgiStr .= "&s3=yes";
    }
    echo ">". $ns3 ."\n";
  }
  echo "</td><td><b>Other Sensors:</b><br>\n";
  echo "<input type=\"checkbox\" name=\"tmpf\" ";
  if (isset($_GET["tmpf"])) {
     echo "CHECKED";
      $cgiStr .= "&tmpf=yes";
    }
  echo ">Air Temperature\n";
  echo "<br><input type=\"checkbox\" name=\"dwpf\" ";
  if (isset($_GET["dwpf"])) {
     echo "CHECKED";
      $cgiStr .= "&dwpf=yes";
    }
  echo ">Dew Point\n";
  echo "<br><input type=\"checkbox\" name=\"subc\" ";
  if (isset($_GET["subc"])) {
     echo "CHECKED";
      $cgiStr .= "&subc=yes";
    }
  echo ">Sub Surface\n";
  echo "</td></tr></table>";

  if (isset($_GET["limit"]))  $cgiStr .= "&limit=yes";

  ?>
  <input type="submit" value="Generate Plot">
  </form>

  <br><img src="SFtemps.php?station=<?php echo $station . $cgiStr; ?>" ALT="Time Series">

<?php
  } else { ?>
  
  <input type="submit" value="Generate Plot">
  </form>
  <p>This application will plot a time series of pavement 
   temperatures for a RWIS station.  Please select the RWIS station from 
   the map below.
  <?php
 echo $swinterface; 

  }
?>


<br><br>

<?php include("$rootpath/include/footer.php"); ?>
