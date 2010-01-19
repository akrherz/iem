<?php
include("../../../config/settings.inc.php");
include ("../../../include/database.inc.php");
$wepp = iemdb("wepp");
$coop = iemdb("coop");

$labels = Array();
$times = Array();
$climate = Array();
$d2009 = Array();
$d2008 = Array();

/* Load up climatology and times arrays */
$rs = pg_query($coop, "SELECT valid, precip from climate51 WHERE 
  station = 'ia0000' and extract(month from valid) IN (4,5,6,7,8,9,10) 
  ORDER by valid ASC");
$r = 0;
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
 $times[] = strtotime( $row["valid"] );
 $r += $row["precip"];
 $climate[] = $r;
 $labels[] = date("d M", strtotime( $row["valid"] ) );
}

/* Load up 2008 from coop */
$rs = pg_query($coop, "SELECT day, precip from alldata WHERE 
  stationid = 'ia0000' and year = 2008 and 
  month IN (4,5,6,7,8,9,10) ORDER by day ASC");
$r = 0;
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
 $r += $row["precip"];
 $d2008[] = $r;
}

/* Load up 2009 estimates from wepp */
$rs = pg_query($wepp, "SELECT valid, sum(rainfall)/8012/25.4 as r from 
      daily_rainfall_2009 d, hrap_polygons h WHERE d.hrap_i = h.hrap_i 
      and valid >= '2009-04-01' and valid < '2009-11-01' GROUP by valid ORDER by valid ASC");
$r = 0;
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
 $r += $row["r"];
 $d2009[] = $r;
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(320,280,"auto");    
$graph->SetScale("textlin");
$graph->legend->Pos(0.05,0.09);
$graph->legend->SetLayout(LEGEND_HOR);

$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetTickLabels( $labels );
$graph->xaxis->SetTextTickInterval( 10 );

$graph->yaxis->title->Set("Accumulated Precip [inch]");
$graph->title->Set("Iowa Precipitation in Apr-Oct");
//$graph->subtitle->Set("For April");

$graph->SetShadow();
$graph->img->SetMargin(40,10,40,60);


// Create the error plot
$lp1=new LinePlot($climate);
$lp1->SetColor("red");
$lp1->SetWeight(2);
$lp1->SetLegend("Climatology");
$graph->Add($lp1);

$lp2=new LinePlot($d2008);
$lp2->SetColor("blue");
$lp2->SetWeight(2);
$lp2->SetLegend("2008");
$graph->Add($lp2);

$lp3=new LinePlot($d2009);
$lp3->SetColor("green");
$lp3->SetWeight(2);
$lp3->SetLegend("2009");
$graph->Add($lp3);


// Display the graph
$graph->Stroke();
?>
