<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connection = iemdb("isuag");

$station = $_GET['station'];
$ts = time() - 86400 - 7*3600;
$table = sprintf("t%s_daily", date("Y", $ts) );
$date = date("Y-m-d", $ts);


$queryData = "c30 as dater, c80 as dater2";
$ylabel = "Temperature [F]";



$query2 = "SELECT ". $queryData .", to_char(valid, 'mm/dd/yy') as valid from ". $table ." WHERE station = '$station' and  
	(valid + '60 days'::interval) > CURRENT_TIMESTAMP  ORDER by valid ASC";

$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$xlabel= array();


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["dater"];
  $ydata2[$i] = $row["dater2"];
  $xlabel[$i] = $row["valid"];
}

pg_close($connection);

include ("$rootpath/include/agclimateLoc.php");
include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph//jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,350,"example1");
$graph->SetScale("textlin");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,40,45,80);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Last 60 daily 4in Soil Temp & Solar Raditaion values for  ". $ISUAGcities[ $station]["city"] );

$graph->title->SetFont(FF_FONT1,FS_BOLD,10);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Month/Day");
$graph->y2axis->SetTitle("Solar Radiation [Langleys]");
$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$graph->y2axis->SetColor("red");
//$graph->yaxis->SetColor("red");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("black");
$lineplot->SetLegend("4in Soil Temp");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetColor("red");
$lineplot2->SetLegend("Solar Rad");


$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");


// Add the plot to the graph
$graph->Add($lineplot);
$graph->AddY2($lineplot2);

// Display the graph
$graph->Stroke();
?>

