<?php
include("../../../include/database.inc.php");

$db = iemdb('squaw');

$rs = pg_exec($db, "SELECT * from real_flow WHERE valid > '2010-08-09' ORDER by valid ASC");

$bankfull = Array();
$flood = Array();
$obs = Array();
$obs1993 = Array();
$times = Array();
$times1993 = Array();
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $times[] = strtotime($row["valid"]);
  $obs[] = $row["cfs"];
  $bankfull[] = 2650;
  $flood[] = 3700;
}

$rs = pg_exec($db, "SELECT * from real_flow WHERE valid > '1993-07-07' and valid < '1993-07-17' ORDER by valid ASC");
$ats = mktime(0,0,0,7,7,1993);
$basets = mktime(0,0,0,8,9,2010);
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $obs1993[] = $row["cfs"];
  $t = strtotime($row["valid"]);
  $times1993[] = ($t - $ats) + $basets;
}


        include_once ("../../../include/jpgraph/jpgraph.php");
        include_once ("../../../include/jpgraph/jpgraph_line.php");
        include_once ("../../../include/jpgraph/jpgraph_plotline.php");
        include_once ("../../../include/jpgraph/jpgraph_date.php");
 
        $graph = new Graph(640,480,"example1");
        $graph->SetScale("datlin");
        $graph->setmargin(60,20,50,100);

        $graph->tabtitle->Set("Squaw Creek at Lincoln Way, Ames");

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->yaxis->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->xaxis->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->legend->SetFont(FF_ARIAL,FS_NORMAL,10);

      //  $graph->xaxis->SetTickLabels($xlabel);
      //  $graph->xaxis->SetTextTickInterval(12); 
 $graph->xaxis->SetLabelAngle(90);
 //$graph->xaxis->SetLabelFormatString("M d h A", true);

function tb($a){
  global $basets, $ats;
  $d1993 = ($a - $basets) + $ats;
  return date("M d", $a) ."/". date("M d", $d1993);
  //return '';
}

$graph->xaxis->SetLabelFormatCallback('tb');
$graph->xaxis-> scale->ticks->Set(21600,86400);

        $graph->yaxis->SetTitle("Flow @ Gauge (cfs)");
        $graph->yaxis->SetTitleMargin(45);

    $graph->legend->Pos(0.01, 0.01);
    $graph->legend->SetLayout(LEGEND_HOR);

$pl = new PlotLine(HORIZONTAL,3700,"green",2);
$pl->SetLegend("Flood");
$graph->AddLine($pl);

$lineplot2=new LinePlot($obs1993, $times1993);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("July 1993");
$lineplot2->SetWeight(3);
$graph->Add($lineplot2);

$lineplot=new LinePlot($obs, $times);
$lineplot->SetColor("red");
$lineplot->SetLegend("August 2010");
$lineplot->SetWeight(3);
$graph->Add($lineplot);

//$graph->img->SetAntiAliasing();

        $graph->Stroke();

?>
