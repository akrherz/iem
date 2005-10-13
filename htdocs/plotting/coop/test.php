<?php
$connection = pg_connect("10.10.10.20","5432","coop");
$connection2 = pg_connect("10.10.10.10","5432","asos");


$query2 = "SELECT max_".$data." as max, min_".$data." as min, ".$data." as avg, years, to_char(valid, 'mm dd') as valid from climate WHERE station = '". $station ."' ORDER by valid ASC";

$query3 = "SELECT max(tmpf) - min(tmpf) as min, to_char(valid, 'mm dd') as tvalid from t1997 
	WHERE station = 'ALO' GROUP by tvalid ORDER by tvalid ASC";

$query2 = "SELECT tmpf - dwpf as diff, to_char(valid, 'mm dd') as tvalid from t1997 
	WHERE date_part('hour', valid) = 5 and station = 'ALO' ORDER by tvalid ASC";


$result = pg_exec($connection2, $query2);
//$result2 = pg_exec($connection2, $query3);

$ydata = array();
$ydata2 = array();
$ydata3 = array();
$ydata4 = array();
$xlabel= array();
$years = 0;


$j = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
//  $ydata[$i]  = $row["max"];
  $ydata2[$i]  = $row["diff"];
//  $ydata3[$i]  = $row["avg"];
  $xlabel[$i]  = "";
  $years = $row["years"];
//  $row2 = @pg_fetch_array($result2,$j);
//  $tester = $row2["valid"];
//  if ($tester == $row["valid"] ){
//    $ydata4[$i] = $row2["min"];
 //   $ydata2[$i]  = $row2["max2"];
//    $ydata3[$i] = $row2["min"];
//    $j = $j + 1;
//  }
}


$xlabel[0] = "Jan 1";  // 1
$xlabel[31] = "Feb 1"; // 32
$xlabel[60] = "Mar 1"; // 61
$xlabel[91] = "Apr 1"; // 92
$xlabel[121] = "May 1"; // 122
$xlabel[152] = "Jun 1"; //153
$xlabel[182] = "Jul 1"; //183
$xlabel[213] = "Aug 1"; //214
$xlabel[244] = "Sept 1"; //245
$xlabel[274] = "Oct 1"; //274
$xlabel[305] = "Nov 1"; //306
$xlabel[335] = "Dec 1"; //336
$xlabel[365] = "Dec 31"; //366

pg_close($connection);
pg_close($connection2);

include ("../dev15/jpgraph.php");
include ("../dev15/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(700,650,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,40,65,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Daily ".$data." Extremes for ". $station);
$graph->subtitle->Set("Climate Record: " . $years ." years");

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Date");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.01, 0.08);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Max ".$data." (F)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("Min ".$data." (F)");
$lineplot2->SetColor("blue");

// Create the linear plot
$lineplot3=new LinePlot($ydata3);
$lineplot3->SetLegend("Average (F)");
$lineplot3->SetColor("brown");

// Create the linear plot
$lineplot4=new LinePlot($ydata4);
$lineplot4->SetLegend("Obs 2001 (F)");
$lineplot4->SetColor("black");

// Add the plot to the graph
//$graph->Add($lineplot);
//$graph->Add($lineplot3);
$graph->Add($lineplot2);
//$graph->Add($lineplot4);

$graph->AddLine(new PlotLine(VERTICAL,31,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,60,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,91,"black",1));
$graph->AddLine(new PlotLine(VERTICAL,121,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,152,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,182,"black",1));
$graph->AddLine(new PlotLine(VERTICAL,213,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,244,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,274,"black",1));
$graph->AddLine(new PlotLine(VERTICAL,305,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,335,"tan",1));
$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));

// Display the graph
$graph->Stroke();
?>

