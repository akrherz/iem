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

$subc = isset($_GET["subc"]) ? $_GET["subc"] : false;
$dwpf = isset($_GET["dwpf"]) ? $_GET["dwpf"] : false;
$tmpf = isset($_GET["tmpf"]) ? $_GET["tmpf"] : false;
$pcpn = isset($_GET["pcpn"]) ? $_GET["pcpn"] : false;
$s0 = isset($_GET["s0"]) ? $_GET["s0"]: false;
$s1 = isset($_GET["s1"]) ? $_GET["s1"]: false;
$s2 = isset($_GET["s2"]) ? $_GET["s2"]: false;
$s3 = isset($_GET["s3"]) ? $_GET["s3"]: false;

if (! $subc && ! $dwpf && ! $tmpf && ! $s0 && ! $s1 && ! $s2 && ! $s3 ){
  $_GET["tmpf"] = "on";
}

include("$rootpath/include/google_keys.php");
include("$rootpath/include/imagemaps.php");
include("$rootpath/include/forms.php");
$api = $GOOGLEKEYS[$rooturl]["any"];
$HEADEXTRA = "<script src='http://maps.google.com/maps?file=api&amp;v=2&amp;key=$api'></script>
<script src='http://www.openlayers.org/api/OpenLayers.js'></script>
<script src='${rooturl}/js/olselect.php?network=IA_RWIS'></script>";
$BODYEXTRA = "onload=\"init()\"";
$TITLE = "IEM | RWIS Timeseries Plots";
$THISPAGE = "networks-rwis";
include("$rootpath/include/header.php"); 
?>
<style type="text/css">
        #map {
            width: 450px;
            height: 450px;
            border: 2px solid black;
        }
</style>


<p>This application plots a timeseries of data from an Iowa RWIS site 
of your choice.  You can optionally select which variables to plot and
for which time period in the archive.</p>

<form method="GET" action="sf_fe.php" name="olselect">

<?php if (strlen($station) > 0 ) {  ?>
<table cellpadding="2" cellspacing="0" border="1">
<tr><th>Select Station</th><th colspan="5">Timespan</th></tr>

<tr><td rowspan="2">
  <?php echo networkSelect("IA_RWIS",$station); ?>
  <br />Or from <a href="sf_fe.php">a map</a></td>

   <td rowspan="2" valign="TOP"><input type="radio" name="mode" value="rt" <?php if ($mode == "rt") echo "CHECKED"; ?>>Current</td>
   <td colspan="4"><input type="radio" name="mode" value="hist" <?php if ($mode == "hist") echo "CHECKED"; ?>>Historical</td></tr>

<tr>
  <td>Start Year:<br /><?php echo yearSelect2(1995, $syear, "syear"); ?></td>
  <td>Start Month:<br /><?php echo monthSelect2($smonth, "smonth"); ?></td>
  <td>Start Day:<br /><?php echo daySelect2($sday, "sday"); ?></td>
  <td>Number of days:<br />
   <select name="days">
     <option value="1" <?php if ($days == "1") echo "SELECTED"; ?>>1
     <option value="2" <?php if ($days == "2") echo "SELECTED"; ?>>2
     <option value="3" <?php if ($days == "3") echo "SELECTED"; ?>>3
     <option value="4" <?php if ($days == "4") echo "SELECTED"; ?>>4
     <option value="5" <?php if ($days == "5") echo "SELECTED"; ?>>5
   </td>
 </tr>
</table>

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
  echo "<table border=\"1\" cellpadding=\"3\" cellspacing=\"0\">
      <tr><th colspan=\"3\">Plot Options</th></tr>
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

  echo "<br><input type=\"checkbox\" name=\"pcpn\" ";
  if (isset($_GET["pcpn"])) {
     echo "CHECKED";
      $cgiStr .= "&pcpn=yes";
    }
  echo ">Precipitation\n";
  echo "</td></tr></table>";

  if (isset($_GET["limit"]))  $cgiStr .= "&limit=yes";

  ?>
  <input type="submit" value="Generate Plot">
  </form>

  <br><img src="SFtemps.php?station=<?php echo $station . $cgiStr; ?>" ALT="Time Series">

<?php
  } else { ?>
  
<table><tr><th>Select Station</th>
<td><?php echo networkSelect("IA_RWIS", ""); ?></td>
<td><input type="submit" value="Make Plot"></tr></table>
<div id="map"></div>
<div id="sname" unselectable="on">No site selected</div>
</form>


  </form>


  <?php
  }
?>


<br><br>

<?php include("$rootpath/include/footer.php"); ?>
