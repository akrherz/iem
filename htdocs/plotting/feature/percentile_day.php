<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$coop = iemdb("coop");
$iem = iemdb("access");

$rs = pg_query($iem, "SELECT day, max_tmpf, min_tmpf from summary WHERE 
                      station = 'DSM' and day >= '2009-06-01' and day < '2009-06-29' ORDER by day ASC");

$hpc = Array();
$lpc = Array();
$dates = Array();
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $x = $row["max_tmpf"];
  $n = $row["min_tmpf"];
  $d = $row["day"];
  $dates[] = strtotime($d);
  $highs = Array(); $lows = Array();
  $sql = sprintf("SELECT high, low from alldata WHERE 
   stationid = 'ia2203' and sday = '%s%s'", substr($d, 5,2), substr($d,8,2));
  $rs2 = pg_query($coop, $sql);
  for($j=0;$row=@pg_fetch_array($rs2,$j);$j++)
  {
    $highs[] = $row["high"]; $lows[] = $row["low"];
  }
  asort($highs); asort($lows);
  $cnt = sizeof($highs);
  $z = 0;
  while( list($k,$v) = each($highs) )
  {
    if ($v > $x){ break; }
    $z++;
  }
  $hpc[] = $z / $cnt * 100;
  $z = 0;
  while( list($k,$v) = each($lows) )
  {
    if ($v > $n){ break; }
    $z++;
  }
  $lpc[] = $z / $cnt * 100;
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin",0,100);
$graph->img->SetMargin(40,5,20,55);

$graph->yaxis->scale->ticks->Set(25,5);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("Md", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
//$graph->xaxis->SetPos("min");

$graph->xaxis->SetTitleMargin(27);

//$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->SetTitle(" 2009");
$graph->yaxis->SetTitle("Percentile");
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Des Moines [KDSM] Temp Percentile');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.5,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new BarPlot($hpc, $dates);
$lineplot->SetLegend("Highs");
$lineplot->SetFillColor("red");
$lineplot->SetWidth(5);
$graph->Add($lineplot);

// Create the linear plot
$lineplot2=new BarPlot($lpc,$dates);
$lineplot2->SetLegend("Lows");
$lineplot2->SetFillColor("blue");
//$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();


?>
