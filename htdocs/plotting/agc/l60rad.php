<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connection = iemdb("campbelldaily");

$station = $_GET['station'];

$table1 = $station ."_2004";
$table2 = $station ."_2005";

$queryData = "c30 as dater, c80 as dater2";
$ylabel = "Temperature [F]";


//if ($plot == "soil"){
//	$queryData = "c300 as dater, c800";
//	$y2label = "4in Soil Temp [F]";
//}

$query2 = "SELECT ". $queryData .", to_char(day, 'mm/dd/yy') as valid from ". $table1 ." WHERE 
	(day + '60 days'::interval) > CURRENT_TIMESTAMP  UNION 
	SELECT ". $queryData .", to_char(day, 'mm/dd/yy') as valid from ". $table2 ." WHERE
	(day + '60 days'::interval) > CURRENT_TIMESTAMP ORDER by valid ASC ";

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

//  $xlabel = array_reverse( $xlabel );
//  $ydata  = array_reverse( $ydata );
//  $ydata2  = array_reverse( $ydata2 );
//  $ydata3  = array_reverse( $ydata3 );

pg_close($connection);

include ("../../include/agclimateLoc.php");
include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,350,"example1");
$graph->SetScale("textlin");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,40,45,80);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
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

