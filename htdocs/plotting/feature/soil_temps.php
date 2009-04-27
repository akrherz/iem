<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$dbconn = iemdb('isuag');
$times = Array();
$highs = Array();
$lows = Array();

$sql = "SELECT extract(doy from valid) as doy, max(c30) as high,
  min(c30) as low from daily WHERE station = 'A130209' and c30_f != 'e' 
  and extract(month from valid) = 4 GROUP by doy 
  ORDER by doy ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = mktime(12,0,0,1,1,2000) + (intval($row["doy"]) * 86400);
  $highs[] = $row["high"] ;
  $lows[] = $row["low"] ;
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(60,5,45,70);
$graph->SetMarginColor('white');
$graph->ygrid->SetLineStyle('dashed');
$graph->xgrid->Show();
$graph->xgrid->SetLineStyle('dashed');

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(70);

$graph->title->Set("4 inch Soil Temperature Range");

$graph->yaxis->SetTitle("Daily Avg Temperature [F]");
$graph->xaxis->SetFont(FF_FONT2,FS_BOLD,16);
$graph->yaxis->SetFont(FF_FONT2,FS_BOLD,16);
$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->subtitle->Set('Ames [1986-2008]');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.6,0.15, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->Show();
  $graph->xgrid->Show();

function tb($a){
  return date('M d', $a);
  //return '';
}

$graph->xaxis->SetLabelFormatCallback('tb');
$graph->xaxis-> scale->ticks->Set(86400,86400*7);

$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",1));
$graph->AddLine(new PlotLine(HORIZONTAL,50,"blue",1));

// Create the linear plot
$lineplot=new LinePlot($highs, $times);
$lineplot->SetFillColor('skyblue@0.2');
$lineplot->SetColor('navy@0.7');
$graph->Add($lineplot);

$lineplot2=new LinePlot($lows, $times);
$lineplot2->SetFillColor('wheat');
$lineplot2->SetColor('navy@0.7');
$graph->Add($lineplot2);



// Display the graph
$graph->Stroke();
?>
