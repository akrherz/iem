<?php

$tableName = "t2003";
$dbName = "asos";
if ( strlen($date) == 0) {
  $dbName = "compare";
  if ( strlen($station) == 3 ) {
    $tableName = "transfer";
  } else {
    $tableName = "rtransfer";
  }
} else {
  $tableName = "t2003";
  if ( strlen($station) == 3 ) {
    $dbName = "asos";
  } else {
    $dbName = "rwis";
  } 
}

if ( strlen($hours) == 0 ){
	$hours = "24";
}

$connection = pg_connect("10.10.10.40","5432", $dbName);


$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT tmpf, dwpf  
	, valid from ". $tableName ." WHERE station = '". $station ."' 
	and valid + '".$hours." hours' > CURRENT_TIMESTAMP ORDER by valid ASC";

// $result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$xlabel= array();

$asos = Array("AMW" => 1, "CID" => 1, "IOW" => 1, "BRL" => 1, 
  "DBQ" => 1, "ALO" => 1, "MCW" => 1, "MIW" => 1,
  "DVN" => 1, "DSM" => 1, "LWD" => 1, "SPW" => 1, 
  "EST" => 1, "SUX" => 1, "OTM" => 1);

$minInterval = 20;
if (strlen($asos[$station]) > 0) {
  $minInterval = 60;
} 

$shouldbe = 0;
$timestep = $minInterval * 60; # 20 minutes

$ai = 0;
$missing = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
#  $ydata[$i]  = $row["tmpf"];
#  $ydata2[$i]  = $row["dwpf"];
#  $xlabel[$i] = $row["valid"];
  $ts = strtotime( $row["valid"] );

  if ($shouldbe == 0){
    $shouldbe = $ts;
  }
#  echo $row["valid"] ." || ". $ts ." || ". $shouldbe ."<br>";
  if ($shouldbe == $ts) {  // Good!!!
    $ydata[$ai] = $row["tmpf"];
    $ydata2[$ai] = $row["dwpf"];
    $xlabel[$ai] = strftime("%d %I %p", $shouldbe);
  }
  else if ($shouldbe < $ts) { // Observation is missing
    while ($shouldbe < $ts) {
      $shouldbe = $shouldbe + $timestep;
#      echo "== ". $row["valid"] ." || ". $ts ." || ". $shouldbe ."<br>";
      $ydata[$ai] = " ";
      $ydata2[$ai] = " ";
      $xlabel[$ai] = strftime("%d %I %p", $shouldbe);
      $ai++;
      $missing++;
    }
    $ydata[$ai] = $row["tmpf"];
    $ydata2[$ai] = $row["dwpf"];
    $xlabel[$ai] = strftime("%I %p", $shouldbe);
  }
  $ai++;
  $shouldbe = $shouldbe + $timestep;
}

pg_close($connection);

include ("../dev19/jpgraph.php");
include ("../dev19/jpgraph_line.php");
include ("../../include/allLoc.php");

// Create the graph. These two calls are always required
$graph = new Graph(200,200,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,5,45,60);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);

$interval = intval( sizeof($xlabel) / 12 );
if ($interval > 1 ){
  $graph->xaxis->SetTextLabelInterval(2);
  $graph->xaxis->SetTextTickInterval($interval);
}
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($cities[$station]['city']);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.02, 0.10);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Temp (F)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("Dwp (F)");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

