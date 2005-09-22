<?php
// 02 Jul 2002:	Cleanup a bit, eh?

$connection = pg_connect("localhost","5432","iowa");

if ( strlen( $tlength) == 0  ){
	$tlength = "24";
}

$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT to_char(valid, 'mmdd/HH24MI') as tvalid, * from std_dev WHERE (valid + '". $tlength ." hours'::interval) > CURRENT_TIMESTAMP ORDER by valid";

$result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$ydata3 = array();
$xlabel= array();

if ($data == "dwpf"){
 $queryStr = "dwpf_";
 $varname = "Dew Point";

} else{
 $queryStr = "";
 $varname = "Temperature";
}


$wegood = "";
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
  $test = $row["asos_". $queryStr ."dev"];
  if ( strlen( $test ) == 0 && $i < 2 && strlen( $wegood ) == 0 ) {  

  } elseif ( strlen( $test ) == 0 && $i < 4 ) {
        $ydata[$i] = "-";
  } elseif ( strlen( $test ) == 0 ) {
	$ydata[$i] = "-";
  } else {
	$wegood = "Yes";
  	$ydata[$i]  = $row["asos_". $queryStr ."dev"];
  }


  $ydata2[$i]  = $row["rwis_". $queryStr ."dev"];
  $ydata3[$i] = $row["awos_". $queryStr ."dev"];
  $xlabel[$i] = $row["tvalid"];
}


pg_close($connection);


include ("../dev17/jpgraph.php");
include ("../dev17/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,10,60,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetTextTickInterval(3);
$graph->legend->SetLayout(LEGEND_HOR);
//$graph->legend->SetBackground("white");
$graph->legend->Pos(0.05, 0.1, "right", "top");

$graph->title->Set("Last ". $tlength ." h Standard Deviations for ".$varname." Obs");
$graph->title->SetFont(FF_VERDANA,FS_BOLD,12);
$graph->yaxis->SetTitle($varname ." STD_DEV (F)");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->xaxis->SetTitle("Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);


// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("ASOS (F)");
$lineplot->SetColor("red");
//$lineplot->SetColor("black");
//$lineplot->SetStyle("longdashed");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("RWIS (F)");
$lineplot2->SetColor("blue");
//$lineplot2->SetColor("black");
//$lineplot2->SetStyle("solid");

// Create the linear plot
$lineplot3=new LinePlot($ydata3);
$lineplot3->SetLegend("AWOS (F)");
$lineplot3->SetColor("black");
//$lineplot3->SetStyle("dotted");


// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);
$graph->Add($lineplot3);

// Display the graph
$graph->Stroke();
?>

