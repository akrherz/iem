<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$coop = iemdb("coop");

$mx = -400; $mn = -400;
$maxline = Array(-400);
$minline = Array(-400);
$xlabels = Array("03");

$rs = pg_query($coop, "SELECT sday, max( gdd50(high,low) ) as top,
      min( gdd50(high,low) ) as bottom from alldata 
      WHERE stationid = 'ia2364' and sday BETWEEN '0904' and '0930'
      GROUP by sday ORDER by sday ASC");
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $mx += $row["top"] - 15;
  $mn += $row["bottom"] - 15;
  $maxline[] = $mx;
  $minline[] = $mn;
  $xlabels[] = substr($row["sday"],2,2);
}
$xlabels[] = " ";

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(300,280);
$graph->SetScale("textlin");
$graph->SetMarginColor('lightblue');
$graph->SetMargin(50,5,50,20);
$graph->SetFrame(true,'darkblue');
// Ticks on the outsid
$graph->xaxis->SetTickSide(SIDE_DOWN);
$graph->yaxis->SetTickSide(SIDE_LEFT);
$graph->xaxis->SetFont(FF_ARIAL,FS_BOLD,7);
$graph->yaxis->SetFont(FF_ARIAL,FS_BOLD,7);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);

$graph->title->Set("Possible to Make up 400 Growing\n Degree Day Departure by 1 Oct?");
$graph->title->SetFont(FF_ARIAL,FS_NORMAL,12);

// Setup the legend box colors and font
$graph->legend->SetColor('white','navy');
$graph->legend->SetFillColor('teal@0.25');
$graph->legend->SetFont(FF_ARIAL,FS_BOLD,7);
$graph->legend->SetShadow('darkgray@0.4',3);
$graph->legend->SetPos(0.2,0.70,'left','top');

$graph->xaxis->SetTickLabels($xlabels);
$graph->xaxis->SetTextTickInterval(2);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitle("Day of September 2009");

$graph->yaxis->SetTitle("Growing Degree Days [base50]");
$graph->yaxis->title->SetMargin(10);




// Create the linear plot
$lineplot=new LinePlot($maxline);
$lineplot->SetLegend("w/ Daily Record Highs");
//$lineplot->SetFillColor('white');
$lineplot->SetColor('red');
$lineplot->SetWeight(3);
$graph->Add($lineplot);

// Create the linear plot
$lineplot2=new LinePlot($minline);
$lineplot2->SetLegend("w/ Daily Record Lows");
//$lineplot2->SetFillColor('skyblue@0.2');
$lineplot2->SetColor('blue');
$lineplot2->SetWeight(3);
$graph->Add($lineplot2);


// Display the graph
$graph->Stroke();

?>
