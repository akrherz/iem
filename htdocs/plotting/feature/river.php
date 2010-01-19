<?php
include("../../../include/database.inc.php");

$db = iemdb('squaw');

$rs = pg_exec($db, "SELECT * from real_flow WHERE valid > '2009-01-01' ORDER by valid ASC");

$bankfull = Array();
$flood = Array();
$obs = Array();
$times = Array();
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $times[] = strtotime($row["valid"]);
  $obs[] = $row["cfs"];
  $bankfull[] = 2650;
  $flood[] = 3700;
}


        include_once ("../../../include/jpgraph/jpgraph.php");
        include_once ("../../../include/jpgraph/jpgraph_line.php");
        include_once ("../../../include/jpgraph/jpgraph_date.php");
 
        $graph = new Graph(1024,480,"example1");
        $graph->SetScale("datlin");
        $graph->setmargin(60,20,50,50);

        $graph->tabtitle->Set("Squaw Creek at Lincoln Way, Ames");

      //  $graph->xaxis->SetTickLabels($xlabel);
      //  $graph->xaxis->SetTextTickInterval(12); 
 $graph->xaxis->SetLabelAngle(90);
 //$graph->xaxis->SetLabelFormatString("M d h A", true);
 $graph->xaxis->SetLabelFormatString("M d", true);

        $graph->yaxis->SetTitle("Flow @ Gauge (cfs)");
        $graph->yaxis->SetTitleMargin(45);

    $graph->legend->Pos(0.01, 0.01);
    $graph->legend->SetLayout(LEGEND_HOR);

        $lineplot=new LinePlot($obs, $times);
        $lineplot->SetColor("red");
        $lineplot->SetLegend("Observed");
        $lineplot->SetWeight(2);

        $lineplot3=new LinePlot($bankfull, $times);
        $lineplot3->SetColor("brown");
        $lineplot3->SetLegend("BankFull(2650)");
        $lineplot3->SetWeight(3);
                                                                          
        $lineplot4=new LinePlot($flood, $times);
        $lineplot4->SetColor("green");
        $lineplot4->SetLegend("Flood(3700)");
        $lineplot4->SetWeight(3);
                                                                          
        $graph->Add($lineplot4);
        $graph->Add($lineplot3);
        $graph->Add($lineplot);
        $graph->Stroke();

?>
