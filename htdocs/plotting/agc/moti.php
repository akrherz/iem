<?php
$connection = pg_connect("localhost","5432","campbelldaily");

$table1 = $station ."_2001";
$table2 = $station ."_2002";

$queryData = "c30 as dater, c80 as dater2, c11 as dater3, c12 as dater4 ";
$ylabel = "Temperature [F]";


//if ($plot == "soil"){
//	$queryData = "c300 as dater, c800";
//	$y2label = "4in Soil Temp [F]";
//}

$query2 = "SELECT ". $queryData .", to_char(day, 'yy/mm/dd') as valid from ". $table1 ." WHERE 
	(day + '60 days'::interval) > CURRENT_TIMESTAMP  UNION 
	SELECT ". $queryData .", to_char(day, 'yy/mm/dd') as valid from ". $table2 ." WHERE
	(day + '60 days'::interval) > CURRENT_TIMESTAMP ORDER by valid ASC ";

$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$ydata3 = array();
$ydata4 = array();
$xlabel= array();


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["dater"];
  $ydata2[$i] = $row["dater2"];
  $ydata3[$i] = $row["dater3"];
  $ydata4[$i] = $row["dater4"];
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
$graph = new Graph(700,550,"example1");
$graph->SetScale("textlin");
$graph->SetMarginColor("white");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,40,45,80);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Last 60 daily 4in Soil Temp & Solar Raditaion values for  ". $ISUAGcities[ $station]["city"] );

$graph->title->SetFont(FF_VERDANA,FS_BOLD,12);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitle("Month/Day");
$graph->y2axis->SetTitle("Solar Radiation [Langleys]");
$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);

$graph->y2axis->SetColor("black");
//$graph->yaxis->SetColor("red");
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("green");
$lineplot->SetLegend("4in Soil Temp");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetColor("black");
$lineplot2->SetLegend("Solar Rad");

// Create the linear plot
$lineplot3=new LinePlot($ydata3);
$lineplot3->SetColor("red");
$lineplot3->SetLegend("High Temp");

// Create the linear plot
$lineplot4=new LinePlot($ydata4);
$lineplot4->SetColor("blue");
$lineplot4->SetLegend("Low Temp");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetBackground("white");
$graph->legend->Pos(0.10, 0.04, "right", "top");


// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot3);
$graph->Add($lineplot4);
$graph->AddY2($lineplot2);

// Display the graph
$graph->Stroke();
?>

