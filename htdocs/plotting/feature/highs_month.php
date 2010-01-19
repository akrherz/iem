<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_error.php");
include ("../../../include/database.inc.php");

$db = iemdb("access");
$coopdb = iemdb("coop");

$errdatay = Array();

$sql = sprintf("SELECT extract(day from day) as d, max(max_tmpf) as x,
       min(max_tmpf)  as n from summary WHERE day < '2009-09-01' and 
       day >= '2009-08-01' and network IN ('IA_ASOS','AWOS') and
       max_tmpf > 50 and max_tmpf < 100 GROUP by d ORDER by d ASC");
$rs = pg_query($db, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $errdatay[] = $row["x"];
  $errdatay[] = $row["n"];
}


$err1936 = Array();

$sql = sprintf("SELECT extract(day from day) as d, max(high) as x,
       min(high)  as n from alldata WHERE day < '1936-09-01' and 
       day >= '1936-08-01' GROUP by d ORDER by d ASC");
$rs = pg_query($coopdb, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $err1936[] = $row["x"];
  $err1936[] = $row["n"];
}



// Create the graph. These two calls are always required
$graph = new Graph(320,300,"auto");    
$graph->SetScale("textlin");
$graph->legend->Pos(0.05,0.08);
$graph->legend->SetLayout(LEGEND_HOR);

$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->title->Set("High Temperature [F]");
$graph->title->Set("Iowa High Temp Range Then & Now");
//$graph->subtitle->Set("For January 2009");

$graph->SetShadow();
$graph->img->SetMargin(40,10,40,40);

//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));

// Create the error plot
$errplot=new ErrorPlot($errdatay);
$errplot->SetColor("blue");
$errplot->SetWeight(2);
$errplot->SetCenter();
$errplot->SetLegend("2009 ASOS+AWOS");
$graph->Add($errplot);

$errplot2=new ErrorPlot($err1936);
$errplot2->SetColor("red");
$errplot2->SetWeight(2);
$errplot2->SetLegend("1936 COOP");
$errplot2->SetCenter();
$graph->Add($errplot2);


// Display the graph
$graph->Stroke();
?>
