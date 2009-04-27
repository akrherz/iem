<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_error.php");
include ("../../../include/database.inc.php");

$db = iemdb("coop");

$errdatay = Array();

$sql = sprintf("SELECT extract(day from day) as d, max(max_tmpf) as x,
       min(max_tmpf)  as n from summary WHERE day < '2009-03-01' and 
       day >= '2009-02-01' and network = 'IA_ASOS' GROUP by d ORDER by d ASC");
$rs = pg_query($db, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $errdatay[] = $row["x"];
  $errdatay[] = $row["n"];
}


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"auto");    
$graph->SetScale("textlin");
$graph->legend->Pos(0.05,0.08);
$graph->legend->SetLayout(LEGEND_HOR);

$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->title->Set("High Temperature [F]");
$graph->title->Set("Iowa ASOS High Temp Range");
$graph->subtitle->Set("For January 2009");

$graph->SetShadow();
$graph->img->SetMargin(40,10,40,40);

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
