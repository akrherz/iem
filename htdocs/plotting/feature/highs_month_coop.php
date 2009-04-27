<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_error.php");
include ("../../../include/database.inc.php");

$db = iemdb("coop");

$xlabel = Array();
$errdatay = Array();

$sql = sprintf("SELECT day, high, low
       from alldata WHERE day BETWEEN '1905-02-10' and '1905-03-06'
       and stationid = 'ia0200'
       ORDER by day ASC");
$rs = pg_query($db, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $errdatay[] = $row["high"];
  $errdatay[] = $row["low"];
  $xlabel[] = substr($row["day"],6,5);
}


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"auto");    
$graph->SetScale("textlin");
$graph->legend->Pos(0.05,0.08);
$graph->legend->SetLayout(LEGEND_HOR);

$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetTickLabels($xlabel);
$graph->yaxis->title->Set("Temperature [F]");
$graph->title->Set("Shortest 100+ deg swing for Ames ");
$graph->subtitle->Set("Feb 13 [-31] till Mar 3 [75] 1905 (18 days)");

$graph->SetShadow();
$graph->img->SetMargin(40,10,40,45);

$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));

// Create the error plot
$errplot=new ErrorPlot($errdatay);
$errplot->SetColor("red");
$errplot->SetWeight(2);
$errplot->SetCenter();

// Add the plot to the graph
$graph->Add($errplot);


// Display the graph
$graph->Stroke();
?>
