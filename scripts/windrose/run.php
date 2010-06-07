<?php
set_time_limit(580);
include_once("../../config/settings.inc.php");
include_once("$rootpath/include/network.php");
include_once("$rootpath/include/database.inc.php");
$nt = new NetworkTable( Array("IA_ASOS") );
$cities = $nt->table;

function windrose_maker($network, $station, $month)
{
  global $cities;
  
  $wp_data = Array();
  $pg_conn = iemdb("asos");

  $total = 0;
  $sumsknt = 0;
  $first_year = 0;

  if ($month == 0) {
    $ts = mktime(0,0,0,1,1,2000);
    $monthSQL = "";
  } else {
    $ts = mktime(0,0,0,$month,1,2000);
    $monthSQL = sprintf("and extract(month from valid) = %s", $month);
  }
  $sql = sprintf("select count(*), sum(sknt) as totsknt, 
  min(valid) as sts, max(valid) as ets,
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
   from alldata
  WHERE 
    sknt >= 0 and drct >= 0 and station = '%s'
    %s
  GROUP by d, s", $station, $monthSQL);
  $rs = pg_query($pg_conn, $sql);

  $sts = mktime(0,0,0,1,1,2020);
  $ets = mktime(0,0,0,1,1,1970);
  for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
  {
    if ( strtotime($row["sts"]) < $sts){ $sts = strtotime($row["sts"]); }
    if ( strtotime($row["ets"]) > $ets){ $ets = strtotime($row["ets"]); }
    $sumsknt += intval($row["totsknt"]);
    $d = $row["d"];
    $s = intval($row["s"]);
    $c = $row["count"];
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
  if ($month > 0){
    $subt = sprintf("During %s for years %s-%s", date("F", $ts), date("Y", $sts), date("Y",$ets) );
    $fp = sprintf("/mesonet/share/windrose/climate/monthly/%s/%s_%s.png", sprintf("%02d",$month), $station, strtolower(date("M",$ts)) );
  } else {  
    $subt = sprintf("During years %s-%s", date("Y", $sts), date("Y",$ets));
    $fp = sprintf("/mesonet/share/windrose/climate/yearly/%s_yearly.png", $station);
  }
 // $graph->title->SetMargin(-20);

  $graph->subtitle->Set( $subt );

  // Create the windrose plot.
  $wp = new WindrosePlot($wp_data);
  $wp->SetRanges(array(2,5,10,15,20,100));
  $wp->legend->SetFormat('%.0f');
  $wp->legend->SetMargin(30);
  $wp->SetRangeColors(array('red','navy','darkgreen','yellow')); 
  //$wp->SetSize(300);


  $icon = new IconPlot('../../htdocs/images/logo_small.gif',0.1,0.1,1,100);
  $icon->SetAnchor('center','center');
  $graph->Add($icon);

  $graph->Add($wp);
  $wp->legend->SetText("Wind speed in knots \n[$total obs, avg ". round($sumsknt/$total,2) ." kts]\nplot generated ". date("d F Y") );
  $wp->scale->SetZeroLabel("Calm\n%d%%"); 
  $graph->Stroke( $fp );

} // End of function


while (list($key,$val) = each($cities))
{
  $network = $val["network"];
  echo "Lets do $key\n";
  for ($k=0;$k<13;$k++)
  {
    windrose_maker('asos', $key, $k);
  }
}
/*
  for ($k=0;$k<13;$k++)
  {
    windrose_maker('asos', 'SUX', $k);
  }
 // windrose_maker('asos', 'FSD', 1);
*/
?>
