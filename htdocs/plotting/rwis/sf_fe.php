<?php
$OL = "6.2.1";
 require_once "../../../config/settings.inc.php";
 require_once "../../../include/myview.php";
 $t = new MyView();
 require_once "../../../include/database.inc.php";
 require_once "../../../include/forms.php";

$network = 'IA_RWIS';
$ostation = isset($_GET["ostation"]) ? xssafe($_GET["ostation"]) : "";
$station = isset($_GET['station']) ? xssafe($_GET["station"]): "";
$mode = isset($_GET["mode"]) ? xssafe($_GET["mode"]): "rt";
$syear = isset($_GET["syear"]) ? xssafe($_GET["syear"]): date("Y");
$smonth = isset($_GET["smonth"]) ? xssafe($_GET["smonth"]): date("m");
$sday = isset($_GET["sday"]) ? xssafe($_GET["sday"]): date("d");
$days = isset($_GET["days"]) ? intval($_GET["days"]): 2;

$subc = isset($_GET["subc"]) ? xssafe($_GET["subc"]): false;
$dwpf = isset($_GET["dwpf"]) ? xssafe($_GET["dwpf"]): false;
$tmpf = isset($_GET["tmpf"]) ? xssafe($_GET["tmpf"]): false;
$pcpn = isset($_GET["pcpn"]) ? xssafe($_GET["pcpn"]): false;
$s0 = isset($_GET["s0"]) ? xssafe($_GET["s0"]): false;
$s1 = isset($_GET["s1"]) ? xssafe($_GET["s1"]): false;
$s2 = isset($_GET["s2"]) ? xssafe($_GET["s2"]): false;
$s3 = isset($_GET["s3"]) ? xssafe($_GET["s3"]): false;

if (! $subc && ! $dwpf && ! $tmpf && ! $s0 && ! $s1 && ! $s2 && ! $s3 ){
  $_GET["tmpf"] = "on";
}

require_once "../../../include/imagemaps.php";
require_once "../../../include/forms.php";
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link rel="stylesheet" type="text/css" href="/vendor/select2/4.0.3/select2.min.css"/ >
EOF;
$t->jsextra = <<<EOF
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src="/js/olselect.php?network=${network}"></script>
<script src="/vendor/select2/4.0.3/select2.min.js"></script>
<script type="text/javascript">
$(document).ready(function(){
	$(".iemselect2").select2();	
});
</script>
EOF;
$t->title = "RWIS Timeseries Plots";
$t->thispage = "networks-rwis";

$content = <<<EOF
<style type="text/css">
        #map {
            width: 450px;
            height: 450px;
            border: 2px solid black;
        }
</style>
<ol class="breadcrumb">
	<li><a href="/RWIS/">RWIS Homepage</a></li>
	<li class="current">RWIS Temperature Time Series Plots</li>
</ol>

<p>This application plots a timeseries of data from an Iowa RWIS site 
of your choice.  You can optionally select which variables to plot and
for which time period in the archive.</p>

<form method="GET" action="sf_fe.php" name="olselect">
EOF;
if (strlen($station) > 0 ) {  
	$ys = yearSelect2(1995, $syear, "syear");
	$ms =  monthSelect2($smonth, "smonth");
	$ds = daySelect2($sday, "sday");
	$ds2 = daySelect2($days, "days");
	$nselect = networkSelect("IA_RWIS",$station);
	
	$c0 = iemdb('rwis');
	$q0 = "SELECT * from sensors WHERE station = '". $station ."' ";
	$r0 = pg_exec($c0, $q0);
	
	$row = pg_fetch_array($r0);
	$ns0 = $row['sensor0'];
	$ns1 = $row['sensor1'];
	$ns2 = $row['sensor2'];
	$ns3 = $row['sensor3'];
	
	pg_close($c0);
	$cgiStr = "&mode=$mode&sday=$sday&smonth=$smonth&syear=$syear&days=$days&";

	$table = "<table class=\"table table-bordered\">
      <tr><th colspan=\"3\">Plot Options</th></tr>
      <tr><td><b>Restrict Plot:</b>
      <br><input type=\"checkbox\" name=\"limit\" value=\"yes\" ";
	if (isset($_GET["limit"])) $table .= "CHECKED";
	$table .= ">Temps between 25-35
    </td><td><b>Pavement Sensors:</b><br>\n";
	if (strlen($ns0) > 0) {
		$table .= "<input type=\"checkbox\" name=\"s0\" ";
		if (isset($_GET["s0"])) {
			$table .= "CHECKED";
			$cgiStr .= "&s0=yes";
		}
		$table .= ">". $ns0 ."\n";
	}
	if (strlen($ns1) > 0) {
		$table .= "<br><input type=\"checkbox\" name=\"s1\" ";
		if (isset($_GET["s1"])) {
			$table .= "CHECKED";
			$cgiStr .= "&s1=yes";
		}
		$table .= ">". $ns1 ."\n";
	}
	if (strlen($ns2) > 0) {
		$table .= "<br><input type=\"checkbox\" name=\"s2\" ";
		if (isset($_GET["s2"])) {
			$table .= "CHECKED";
			$cgiStr .= "&s2=yes";
		}
		$table .= ">". $ns2 ."\n";
	}
	if (strlen($ns3) > 0) {
		$table .= "<br><input type=\"checkbox\" name=\"s3\" ";
		if (isset($_GET["s3"])) {
			$table .= "CHECKED";
			$cgiStr .= "&s3=yes";
		}
		$table .= ">". $ns3 ."\n";
	}
	$table .= "</td><td><b>Other Sensors:</b><br>\n";
	$table .= "<input type=\"checkbox\" name=\"tmpf\" ";
	if (isset($_GET["tmpf"])) {
		$table .= "CHECKED";
		$cgiStr .= "&tmpf=yes";
	}
	$table .= ">Air Temperature\n";
	$table .= "<br><input type=\"checkbox\" name=\"dwpf\" ";
	if (isset($_GET["dwpf"])) {
		$table .= "CHECKED";
		$cgiStr .= "&dwpf=yes";
	}
	$table .= ">Dew Point\n";
	$table .= "<br><input type=\"checkbox\" name=\"subc\" ";
	if (isset($_GET["subc"])) {
		$table .= "CHECKED";
		$cgiStr .= "&subc=yes";
	}
	$table .= ">Sub Surface\n";
	
	$table .= "<br><input type=\"checkbox\" name=\"pcpn\" ";
	if (isset($_GET["pcpn"])) {
		$table .= "CHECKED";
		$cgiStr .= "&pcpn=yes";
	}
	$table .= ">Precipitation\n";
	$table .= "</td></tr></table>";
	
	if (isset($_GET["limit"]))  $cgiStr .= "&limit=yes";
	
	$rtcheck = ($mode == "rt") ? " CHECKED": "";
	$hcheck = ($mode == "hist") ? " CHECKED": ""; 
$content .= <<<EOF
<table class="table table-bordered">
<thead>
<tr><th>Select Station</th><th colspan="5">Timespan</th></tr>
</thead>
<tbody>
<tr><td rowspan="2">
  {$nselect}
  <br />Or from <a href="sf_fe.php">a map</a></td>

   <td rowspan="2" valign="TOP">
  <input type="radio" name="mode" value="rt"{$rtcheck}>Current</td>
   <td colspan="4"><input type="radio" name="mode" value="hist"{$hcheck}>Historical</td></tr>

<tr>
  <td>Start Year:<br />{$ys}</td>
  <td>Start Month:<br />{$ms}</td>
  <td>Start Day:<br />{$ds}</td>
  <td>Number of days:<br />{$ds2}
   </td>
 </tr>
</tbody>
</table>


{$table}

  <input type="submit" value="Generate Plot">
  </form>

 <br><img src="SFtemps.php?station={$station}{$cgiStr}" alt="Time Series" class="img img-responsive"/>
<br><img src="plot_traffic.php?station={$station}{$cgiStr}" alt="Time Series" class="img img-responsive"/>
<br><img src="plot_soil.php?station={$station}{$cgiStr}" alt="Time Series" class="img img-responsive"/>
EOF;
  } else { 
  $nselect = networkSelect("IA_RWIS", "");
$content .= <<<EOF
<input type="hidden" name="s0" value="yes" />
<input type="hidden" name="s1" value="yes" />
<input type="hidden" name="s2" value="yes" />
<input type="hidden" name="s3" value="yes" />
<input type="hidden" name="tmpf" value="yes" />
<input type="hidden" name="dwpf" value="yes" />
<table><tr><th>Select Station</th>
<td>{$nselect}</td>
<td><input type="submit" value="Make Plot"></tr></table>
<div id="map"></div>
</form>


  </form>

EOF;
  }
$t->content = $content;
$t->render('single.phtml');
?>