<?php
set_time_limit(580);

$day1 = isset($_GET["day1"]) ? $_GET["day1"] : die();
$day2 = isset($_GET["day2"]) ? $_GET["day2"] : die();
$month1 = isset($_GET["month1"]) ? $_GET["month1"]: die();
$month2 = isset($_GET["month2"]) ? $_GET["month2"]: die();
$year1 = isset($_GET["year1"]) ? $_GET["year1"] : die();
$year2 = isset($_GET["year2"]) ? $_GET["year2"] : die();
$hour1 = isset($_GET["hour1"]) ? $_GET["hour1"]: die();
$hour2 = isset($_GET["hour2"]) ? $_GET["hour2"]: die();
$minute1 = isset($_GET["minute1"]) ? $_GET["minute1"]: die();
$minute2 = isset($_GET["minute2"]) ? $_GET["minute2"]: die();
$station = isset($_GET["station"]) ? $_GET["station"] : die();
$network = isset($_GET["network"]) ? $_GET["network"] : die();

include("../../config/settings.inc.php");
include("$rootpath/include/station.php");
$st = new StationData($station);
$cities = $st->table;

  $sts = mktime($hour1,$minute1,0,$month1,$day1,$year1);
  $ets = mktime($hour2,$minute2,0,$month2,$day2,$year2);

  $wp_data = Array();
  //$table = "t". date("Y", $sts); 
  $table = "alldata";
  if (strpos($network, "ASOS") > 0) $pg_conn = iemdb("asos");
  elseif (strpos($network, "RWIS") > 0) $pg_conn = iemdb("rwis");
  elseif ($network == "AWOS") {
    $pg_conn = iemdb("awos");
    //$table = "t". date("Y_m", $sts);
    //$ets2 = mktime($hour2,$minute2,0,$month1,$day2,$year);
  }
  elseif ($network == "KCCI" or $network == "KELO" or $network == "KIMT") {
    $pg_conn = iemdb("snet");
    //$table = "t". date("Y_m", $sts);
    //$ets2 = mktime($hour2,$minute2,0,$month1,$day2,$year);
  }

  $hourLimiter = "";
  $hourLimitSubTitle = "";
  if (isset($_GET["hourlimit"]))
  {
   $hourLimiter = " and extract(hour from valid) = ". date("H", $sts);
   $hourLimitSubTitle = "Obs restricted to obs during hour: ". strtoupper(date("h a", $sts));
  }
  $rs = pg_prepare($pg_conn, "SELECT", "select count(*), sum(sknt) as totsknt,
  case 
    when drct > 349 or drct < 14 THEN 'N' 
    when drct BETWEEN 13 and 35 THEN 'NNE' 
    WHEN drct BETWEEN 35 and 57 THEN 'NE' 
    WHEN drct BETWEEN 57 and 80 THEN 'ENE' 
    WHEN drct BETWEEN 80 and 102 THEN 'E' 
    WHEN drct BETWEEN 102 and 127 THEN 'ESE' 
    WHEN drct BETWEEN 127 and 143 THEN 'SE' 
    WHEN drct BETWEEN 143 and 166 THEN 'SSE' 
    WHEN drct BETWEEN 166 and 190 THEN 'S' 
    WHEN drct BETWEEN 190 and 215 THEN 'SSW' 
    WHEN drct BETWEEN 215 and 237 THEN 'SW' 
    WHEN drct BETWEEN 237 and 260 THEN 'WSW' 
    WHEN drct BETWEEN 260 and 281 THEN 'W' 
    WHEN drct BETWEEN 281 and 304 THEN 'WNW' 
    WHEN drct BETWEEN 304 and 324 THEN 'NW' 
    WHEN drct BETWEEN 324 and 350 THEN 'NNW' 
  END as d,
  CASE
    WHEN sknt BETWEEN 0 and 2 THEN 0
    WHEN sknt BETWEEN 2 and 5 THEN 1
    WHEN sknt BETWEEN 5 and 10 THEN 2
    WHEN sknt BETWEEN 10 and 15 THEN 3
    WHEN sknt BETWEEN 15 and 20 THEN 4
    WHEN sknt > 20 THEN 5
  END as s
   from $table
  WHERE 
    sknt >= 0 and drct >= 0 and station = $1
    and valid BETWEEN $2 and $3 $hourLimiter
  GROUP by d, s");
  $rs = pg_execute($pg_conn, "SELECT", Array($station, date("Y-m-d H:i:s", $sts), date("Y-m-d H:i:s", $ets) ) );

  $sumsknt = 0;
  $total = 0;
  for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
  {
    $sumsknt += intval($row["totsknt"]);
    $d = $row["d"];
    $s = intval($row["s"]);
    $c = $row["count"];
    //if ($d == "S") echo "$yr speed: $s count: $c\n";
    $total += $c;
    if (! array_key_exists($d, $wp_data)) $wp_data[$d] = Array(0,0,0,0,0,0);
    $wp_data[$d][$s] += $c;
  }

  reset($wp_data);
  $k = 0;
  while( list($key,$val) = each($wp_data) )
  {
    for($i=0;$i<6;$i++){
      $wp_data[$key][$i] = $wp_data[$key][$i]/$total *100; 
      $k += $wp_data[$key][$i];
    }
  }

  require_once ('/mesonet/share/jpgraph/jpgraph.php');
  require_once ('/mesonet/share/jpgraph/jpgraph_iconplot.php');
  require_once ('/mesonet/share/jpgraph/jpgraph_windrose.php');

  // First create a new windrose graph with a title
  $graph = new WindroseGraph(480,480);
  $graph->title->Set($cities[$station]['name'] ." [$station] Windrose Plot");
  $subt = sprintf("During %s - %s \n $hourLimitSubTitle", date("Y-m-d H:i a", $sts), date("Y-m-d H:i a", $ets) );
  $graph->title->SetMargin(-22);

  $graph->subtitle->Set( $subt );

  // Create the windrose plot.
  $wp = new WindrosePlot($wp_data);
  $wp->SetRanges(array(2,5,10,15,20,100));
  $wp->legend->SetFormat('%.0f');
  $wp->legend->SetMargin(30);
  $wp->SetRangeColors(array('red','navy','darkgreen','yellow')); 
  //$wp->SetSize(300);


  $icon = new IconPlot("$rootpath/htdocs/images/logo_small.gif",0.05,0.01,1,100);
  $icon->SetAnchor('center','center');
  $graph->Add($icon);

  $graph->Add($wp);
  if ($total == 0) $total = 1;
  $wp->legend->SetText("Wind speed in knots \n[$total obs, avg ". round($sumsknt/$total,2) ." kts]\nplot generated ". date("d F Y") );
  $wp->scale->SetZeroLabel( "Calm %d%%"); 

  $graph->Stroke();

?>
