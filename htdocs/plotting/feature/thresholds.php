<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/all_locs.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$times2 = Array();
$cnt = Array();
$cnt2 = Array();

$dbconn = iemdb('coop');
$sql = "select sday, count(*) from alldata WHERE sday != '0229' and stationid = 'ia0200' and high < 40 and sday > '0901' GROUP by sday ORDER by sday ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = mktime(0,0,0,intval(substr($row["sday"],0,2)),intval(substr($row["sday"],2,2)),2000);
  $cnt[] = $row["count"] / 115 * 100;
}

$sql = "select sday, count(*) from alldata WHERE sday != '0229' and stationid = 'ia0200' and high > 70 and sday > '0901' GROUP by sday ORDER by sday ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times2[] = mktime(0,0,0,intval(substr($row["sday"],0,2)),intval(substr($row["sday"],2,2)),2000);
  $cnt2[] = $row["count"] / 115 * 100;
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(40,5,15,50);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(40);


$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Ames, Percent of Years [%]");
//$graph->tabtitle->Set('Recent Comparison');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.35,0.05, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($cnt, $times);
$lineplot->SetLegend("High below 40");
$lineplot->SetColor("blue");

// Create the linear plot
$lineplot2=new LinePlot($cnt2,$times2);
$lineplot2->SetLegend("High above 70");
$lineplot2->SetColor("red");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>
