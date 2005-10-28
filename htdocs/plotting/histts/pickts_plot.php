<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connection = iemdb("asos");
$connection2 = iemdb("rwis");

$station = isset($_GET["station"]) ? $_GET["station"]: "";
$network = isset($_GET["network"]) ? $_GET["network"]: "IA_ASOS";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"]: date("d");
$shour = isset($_GET["shour"]) ? $_GET["shour"]: 0;
$duration = isset($_GET["duration"])? $_GET["duration"]: 12;

$stime = $year ."-". $month ."-". $day ." ". $shour .":00:00";

$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT tmpf, dwpf, to_char(valid, 'yymmdd/HH24MI') as valid from t". $year ." WHERE station = '". $station ."' 
	and valid BETWEEN '". $stime ."' and  ('". $stime ."'::timestamp + '". $duration ." hours'::interval ) ORDER by valid ASC ";

if ( strlen($station) == 3 ) {	
	$result = pg_exec($connection, $query1);
	$result = pg_exec($connection, $query2);
} else {
        $result = pg_exec($connection2, $query1);
        $result = pg_exec($connection2, $query2);
}

$ydata = array();
$ydata2 = array();
$xlabel= array();

$totCount = pg_numrows($result);
$j = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["tmpf"];
  $ydata2[$i]  = $row["dwpf"];
  if ($i % 3 == 0 && $totCount > 48 ){
  	$xlabel[$j] = $row["valid"];
  	$j++;
  } else {
	$xlabel[$i] = $row["valid"];
  }
}

//  $xlabel = array_reverse( $xlabel );
//  $ydata2 = array_reverse( $ydata2 );
//  $ydata  = array_reverse( $ydata );
 

pg_close($connection);
pg_close($connection2);


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(550,300,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,10,20,100);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetPos("min");
if ( $totCount > 48 ){
	$graph->xaxis->SetTextTicks(3);
}
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set( $duration ."h Meteogram for ". $station);

$graph->yaxis->SetTitle("Degree (F)");
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.01);

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

