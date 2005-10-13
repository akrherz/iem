<?php
$station = $_GET['station'];

$tableName = "t2003";
$dbName = "asos";
if ( strlen($date) == 0) {
  $dbName = "iowa";
  if ( strlen($station) == 3 ) {
    $tableName = "azos";
  } else {
    $tableName = "rwis";
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
$query2 = "SELECT sknt, drct,
	valid from ".$tableName." WHERE station = '". $station ."' 
	and valid + '".$hours." hours' > CURRENT_TIMESTAMP ORDER by valid ASC";

// $result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);

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


$ydata = array();
$ydata2 = array();
$xlabel= array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ts = strtotime( $row["valid"] );

  if ($shouldbe == 0){
    $shouldbe = $ts;
  }
#  echo $row["valid"] ." || ". $ts ." || ". $shouldbe ."<br>";
  if ($shouldbe == $ts) {  // Good!!!
    $ydata[$ai] = $row["sknt"];
    $ydata2[$ai] = $row["drct"];
    $xlabel[$ai] = strftime("%m/%d %I %p", $shouldbe);
  }
  else if ($shouldbe < $ts) { // Observation is missing
    while ($shouldbe < $ts) {
      $shouldbe = $shouldbe + $timestep;
#      echo "== ". $row["valid"] ." || ". $ts ." || ". $shouldbe ."<br>";
      $ydata[$ai] = " ";
      $ydata2[$ai] = "-9999";
      $xlabel[$ai] = strftime("%m/%d %I %p", $shouldbe);
      $ai++;
      $missing++;
    }
    $ydata[$ai] = $row["sknt"];
    $ydata2[$ai] = $row["drct"];
    $xlabel[$ai] = strftime("%m/%d %I %p", $shouldbe);
  }
  $ai++;
  $shouldbe = $shouldbe + $timestep;
}

pg_close($connection);


include ("../jpgraph/jpgraph.php");
include ("../jpgraph/jpgraph_line.php");
include ("../jpgraph/jpgraph_scatter.php");
include ("../../include/allLoc.php");


// Create the graph. These two calls are always required
$graph = new Graph(400,350,"example1");
$graph->SetScale("textlin", 0, 50);
$graph->yaxis->scale->ticks->Set(5,1);
//$graph->yaxis->scale->ticks->SetPrecision(0);
$graph->SetY2Scale("lin", 0, 360);
$graph->y2axis->scale->ticks->Set(30,15);
//$graph->y2axis->scale->ticks->SetPrecision(0);
$graph->img->SetMargin(40,40,25,90);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($hours." h winds for ". $cities[$station]['city']);

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle("Wind Speed [knots]");
$graph->y2axis->SetTitle("Direction [N 0]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$interval = intval( sizeof($xlabel) / 12 );
if ($interval > 1 ){
  $graph->xaxis->SetTextLabelInterval(2);
  $graph->xaxis->SetTextTickInterval($interval);
}


$graph->legend->Pos(0.01, 0.07);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($ydata);
// $lineplot->SetLegend("Temp (F)");
$lineplot->SetColor("red");

// Create the linear plot
$sp1=new ScatterPlot($ydata2);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);
// $lineplot2->SetLegend("Dwp (F)");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->AddY2($sp1);

// Display the graph
$graph->Stroke();
?>

