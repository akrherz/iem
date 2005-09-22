<?php
$station = $_GET['station'];
$connection = pg_connect("10.10.10.40","5432","campbellhourly");

$table = $station ."_2005";

$queryData = "c100 as dater, c300 as dater2, c800";
$y2label = "Temperature [F]";


//if ($plot == "soil"){
//	$queryData = "c300 as dater, c800";
//	$y2label = "4in Soil Temp [F]";
//}

if ( strlen($date) == 0){
	$date = "Yesterday";
}

$query2 = "SELECT ". $queryData .", to_char(day, 'mmdd/HH24') as valid from ". $table ." WHERE 
	date(day) = '". $date ."'::date ORDER by day DESC ";

$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$ydata3 = array();
$xlabel= array();


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["c800"];
  $ydata2[$i]  = $row["dater"];
  $ydata3[$i] = $row["dater2"];
  $xlabel[$i] = $row["valid"];
}

  $xlabel = array_reverse( $xlabel );
  $ydata  = array_reverse( $ydata );
  $ydata2  = array_reverse( $ydata2 );
  $ydata3  = array_reverse( $ydata3 );

pg_close($connection);

include ("../../include/agclimateLoc.php");
include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(400,350,"example1");
$graph->SetScale("textlin");
$graph->SetY2Scale("lin",0,1000);
$graph->img->SetMargin(50,40,45,90);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->title->Set($date ." Solar Rad & Temps for  ". $ISUAGcities[ $station]["city"] );

$graph->y2axis->scale->ticks->Set(100,50);
$graph->y2axis->scale->ticks->SetPrecision(0);


$graph->title->SetFont(FF_VERDANA,FS_BOLD,12);
$graph->y2axis->SetTitle("Solar Radiation [kilo-calorie m**-2]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->yaxis->SetTitle( $y2label );
$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(55);
$graph->yaxis->SetTitleMargin(37);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);

//$graph->y2axis->SetColor("blue");
$graph->y2axis->SetColor("red");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("red");
$lineplot->SetLegend("Solar Rad");
$lineplot->SetWeight(2);

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("Air Temp");
$lineplot2->SetWeight(2);

// Create the linear plot
$lineplot3=new LinePlot($ydata3);
$lineplot3->SetColor("green");
$lineplot3->SetLegend("4in Soil Temp");
$lineplot3->SetWeight(2);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");


// Add the plot to the graph
$graph->Add($lineplot2);
$graph->Add($lineplot3);
$graph->AddY2($lineplot);

// Display the graph
$graph->Stroke();
?>

