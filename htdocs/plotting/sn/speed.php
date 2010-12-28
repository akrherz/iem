<?php
/* Generate a ground speed estimate plot from SN data
 */
include ("../../../config/settings.inc.php");
include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/database.inc.php");
$postgis = iemdb("postgis");
pg_query($postgis, "SET TIME ZONE 'GMT'");

$spotter = isset($_GET["spotter"]) ? substr($_GET["spotter"],0,50): "Bart Comstock";
$syear = isset($_GET["syear"]) ? intval($_GET["syear"]) : date("Y");
$smonth = isset($_GET["smonth"]) ? intval($_GET["smonth"]) : date("m");
$sday = isset($_GET["sday"]) ? intval($_GET["sday"]) : date("d");
$shour = isset($_GET["shour"]) ? intval($_GET["shour"]) : 0;
$eyear = isset($_GET["eyear"]) ? intval($_GET["eyear"]) : date("Y");
$emonth = isset($_GET["emonth"]) ? intval($_GET["emonth"]) : date("m");
$eday = isset($_GET["eday"]) ? intval($_GET["eday"]) : date("d");
$ehour = isset($_GET["ehour"]) ? intval($_GET["ehour"]) : 23;

$rs = pg_prepare($postgis, "SELECT", "SELECT x(geom) as lon, y(geom) as lat, 
  valid from spotternetwork_$syear WHERE valid BETWEEN 
  $1 and $2 and name = $3 ORDER by valid ASC");

$sts = mktime($shour, 0, 0, $smonth, $sday, $syear);
$ets = mktime($ehour, 0, 0, $emonth, $eday, $eyear);

function tb($a){
  return date('M d H', $a) ."Z";
  //return '';
}


function haversine($lon0, $lon1, $lat0, $lat1){

    $radius = 6371.0;

    $dlat = deg2rad($lat1-$lat0);
    $dlon = deg2rad($lon1-$lon0);
    $a = sin($dlat/2.) * sin($dlat/2.) + cos(deg2rad($lat0)) * cos(deg2rad($lat1)) * sin($dlon/2.) * sin($dlon/2.);
    $c = 2. * atan2(sqrt($a), sqrt(1.-$a));
    $d = ($radius * $c) > 120 ? "": $radius * $c;
    return $d;

}

$rs = pg_execute($postgis, "SELECT", Array( date("Y-m-d H:i", $sts),
      date("Y-m-d H:i", $ets), $spotter));

$spderr = 0;
$distance = 0;
$times = Array();
$speeds = Array();
$row = pg_fetch_array($rs,0);
$olat = $row["lat"];
$olon = $row["lon"];
$ovalid = strtotime($row["valid"]);
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $ts = strtotime(substr($row["valid"],0,19));
  $distkm = haversine($olon, $row["lon"], $olat, $row["lat"]);
  $deltat = $ts - $ovalid;
  if ($deltat > 0){
    $mph = $distkm / $deltat * 3600.0 * 0.621371192;
  } else {
    $mph = 0;
  }
  if ($mph > 120){
    $spderr += 1;
    $mph = 0;
  } else {
    $distance += $distkm * 0.621371192;
  }

  $times[] = $ts;
  $speeds[] = $mph;
  $olon = $row["lon"];
  $olat = $row["lat"];
  $ovalid = $ts;
}


// Set the basic parameters of the graph 
$graph = new Graph(640,480);
$graph->SetScale("datelin",0,120);
$graph->img->SetAntiAliasing();


// No frame around the image
$graph->SetFrame(false);

// Rotate graph 90 degrees and set margin
$graph->SetMargin(50,5,50,100);

// Set white margin color
$graph->SetMarginColor('white');

// Use a box around the plot area
$graph->SetBox();

// Use a gradient to fill the plot area
//$graph->SetBackgroundGradient('blue','lightblue',GRAD_HOR,BGRAD_PLOT);

// Setup title
$graph->title->Set("SpotterNetwork Report for [$spotter]");
$subt = sprintf("Observations: %s QC Errors: %s Distance: %.1f miles\nPlot Between Dates %s and %s UTC", 
	pg_num_rows($rs), $spderr, $distance, date("Y-m-d H:i", $sts),date("Y-m-d H:i", $ets) );
$graph->subtitle->Set( $subt );
$graph->title->SetFont(FF_VERDANA,FS_BOLD,12);
$graph->subtitle->SetFont(FF_VERDANA,FS_BOLD,10);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatCallback('tb');

// Setup X-axis
//$graph->xaxis->SetTickLabels($datax);
//$graph->xaxis->SetFont(FF_VERDANA,FS_NORMAL,12);

// Some extra margin looks nicer
$graph->xaxis->SetLabelMargin(30);

// Label align for X-axis
$graph->xaxis->SetLabelAlign('right','center');
$graph->xaxis->SetPos("min");

$graph->yaxis->SetTitle("Speed [mph]");
$graph->yaxis->title->SetFont(FF_VERDANA,FS_NORMAL,12);
$graph->yaxis->SetTitleMargin(30);

// Add some grace to y-axis so the bars doesn't go
// all the way to the end of the plot area
//$graph->yaxis->scale->SetGrace(20);

// We don't want to display Y-axis
//$graph->yaxis->Hide();

$graph->legend->Pos(0.1,0.92);
$graph->legend->SetLayout(LEGEND_HOR);


// Now create a bar pot
$bplot = new BarPlot($speeds, $times);
//$bplot->SetShadow();
//$bplot->SetFillGradient('orange','red',GRAD_HOR);
//$bplot->value->Show();
//$bplot->value->SetFont(FF_ARIAL,FS_BOLD,10);
//$bplot->value->SetAlign('left','center');
//$bplot->value->SetColor("white");
//$bplot->value->SetFormat('%.0f');
//$bplot->SetLegend("2008");
//$bplot->SetValuePos('max');

$graph->Add($bplot);

// Add some explanation text
//$txt = new Text("* IEM Computed [1893-2010]");
//$txt->SetPos(1,-5);
//$txt->SetFont(FF_COMIC,FS_NORMAL,10);
//$graph->Add($txt);

// .. and stroke the graph
$graph->Stroke();


?>
