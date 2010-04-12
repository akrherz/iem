<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$coop = iemdb("coop");
$iem = iemdb("access");

$rs = pg_query($iem, "SELECT day, max_tmpf, min_tmpf from summary_2010 WHERE 
                      station = 'AMW' and day >= '2010-03-01' 
                      and day < '2010-04-01' ORDER by day ASC");

$hpc = Array();
$lpc = Array();
$dates = Array();
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $x = $row["max_tmpf"];
  $n = $row["min_tmpf"];
  $d = $row["day"];
  $dates[] = date("d", strtotime($d));
  $highs = Array(); $lows = Array();
  $sql = sprintf("SELECT high, low from alldata WHERE 
   stationid = 'ia0200' and sday = '%s%s'", substr($d, 5,2), substr($d,8,2));
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
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_mgraph.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,300,"example1");
$graph->SetScale("textlin",0,100);
$graph->img->SetMargin(30,5,20,20);
$graph->SetMarginColor('white');
$graph->SetBox(); 
$graph->SetFrame(false);

$graph->ygrid->SetFill(true,'#DDDDDD@0.5','#BBBBBB@0.5');
$graph->ygrid->SetLineStyle('dashed');
$graph->ygrid->SetColor('gray');
$graph->xgrid->Show();
$graph->xgrid->SetLineStyle('dashed');
$graph->xgrid->SetColor('gray');

$graph->yaxis->scale->ticks->Set(25,5);

//$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetTickLabels($dates);
$graph->xaxis->SetTextTickInterval( 2 );

$graph->title->Set('Ames [KAMW] 2010 March');
$graph->title->SetFont(FF_ARIAL,FS_NORMAL,14);
$graph->subtitle->Set('High Temperature Percentile');
$graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
//$graph->AddLine(new PlotLine(VERTICAL,31,"black",2));

$band=new PlotBand(VERTICAL,BAND_SOLID,31,43,"green");
$band->ShowFrame(false);
$graph->Add($band);

// Create the linear plot
$lineplot=new BarPlot($hpc);
//$lineplot->SetLegend("Highs");
$lineplot->SetFillColor("red");
$lineplot->SetWidth(5);
$graph->Add($lineplot);


$graph2 = new Graph(640,260);
$graph2->SetScale("textlin",0,100);
$graph2->img->SetMargin(30,5,20,22);
$graph2->SetMarginColor('white');
$graph2->SetBox();
$graph2->SetFrame(false);
$graph2->ygrid->SetFill(true,'#DDDDDD@0.5','#BBBBBB@0.5');
$graph2->ygrid->SetLineStyle('dashed');
$graph2->ygrid->SetColor('gray');
$graph2->xgrid->Show();
$graph2->xgrid->SetLineStyle('dashed');
$graph2->xgrid->SetColor('gray');
$graph2->title->Set('Low Temperature Percentile');
$graph2->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph2->yaxis->scale->ticks->Set(25,5);
$graph2->xaxis->SetTextTickInterval( 2 );
$graph2->xaxis->SetTickLabels($dates);

$band2=new PlotBand(VERTICAL,BAND_SOLID,31,43,"green");
$band2->ShowFrame(false);
$graph2->Add($band2);

// Create the linear plot
$lineplot2=new BarPlot($lpc);
$lineplot2->SetFillColor("blue");
$lineplot2->SetWidth(5);
$graph2->Add($lineplot2);


/* Multi Graph */
$mgraph = new MGraph();
$mgraph->SetMargin(2,2,2,2);
$mgraph->SetFrame(true,'darkgray',2);
$mgraph->AddMix($graph,0,0);
$mgraph->AddMix($graph2,0,300);
$mgraph->Stroke();

?>
