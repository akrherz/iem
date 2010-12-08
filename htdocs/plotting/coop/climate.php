<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connection = iemdb("coop");
$station1 = isset($_GET["station1"]) ? strtolower($_GET["station1"]) : die("At least 1 station needs to be specified");
$station2 = isset($_GET["station2"]) ? strtolower($_GET["station2"]) : false;

$st1_hi = array();
$st1_lo = array();
$st2_hi = array();
$st2_lo = array();
$xlabel= array();
$years = 51;


$rs = pg_prepare($connection, "SELECT", "SELECT high, low, years, " .
		"to_char(valid, 'mm dd') as valid from climate51 " .
		"WHERE station = $1 ORDER by valid ASC");
$result1 = pg_execute($connection, "SELECT", Array( $station1 ));
for( $i=0; $row = @pg_fetch_array($result1,$i); $i++) 
{ 
  $st1_hi[$i]  = $row["high"];
  $st1_lo[$i]  = $row["low"];
  $xlabel[$i]  = "";
}


if ($station2) {
	$rs = pg_prepare($connection, "SELECT2", "SELECT high, low, years, " .
		"to_char(valid, 'mm dd') as valid from climate51 " .
		"WHERE station = $1 ORDER by valid ASC");
    $result2 = pg_execute($connection, "SELECT2", Array( $station2 ));
	

  for( $i=0; $row = @pg_fetch_array($result2,$i); $i++) 
  { 
    $st2_hi[$i]  = $row["high"];
    $st2_lo[$i]  = $row["low"];
  }
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

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");
include("$rootpath/include/network.php");     
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;
$cities["IOWA"] = Array("name" => "Iowa Statewide");

// Create the graph. These two calls are always required
$graph = new Graph(640,480);
$graph->SetScale("textlin");
$graph->img->SetMargin(40,40,55,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Average Daily High and Low Temperatures");
$graph->subtitle->Set("Climate Record: 1951 - ". date("Y") );

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Date");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.01, 0.07);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($st1_hi);
$graph->Add($lineplot);
$lineplot->SetLegend($cities[strtoupper($station1)]["name"] ." High");
$lineplot->SetColor("red");
$lineplot->SetWeight(2);

// Create the linear plot
$lineplot2=new LinePlot($st1_lo);
$graph->Add($lineplot2);
$lineplot2->SetLegend($cities[strtoupper($station1)]["name"] ." Low");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(2);

// Add the plot to the graph



if ($station2){
  // Create the linear plot
  $lineplot3=new LinePlot($st2_hi);
  $graph->Add($lineplot3);
  $lineplot3->SetLegend($cities[strtoupper($station2)]["name"] ." High");
  $lineplot3->SetColor("brown");
  $lineplot3->SetWeight(2);

  // Create the linear plot
  $lineplot4=new LinePlot($st2_lo);
  $graph->Add($lineplot4);
  $lineplot4->SetLegend($cities[strtoupper($station2)]["name"] ." Low");
  $lineplot4->SetColor("purple");
  $lineplot4->SetWeight(2);

  // Add the plot to the graph
  
  
 
}

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

