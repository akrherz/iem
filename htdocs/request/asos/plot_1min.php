<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";

$sqlStr = "SELECT station, ";
for ($i=0; $i< $num_vars;$i++){
  $sqlStr .= $vars[$i] ." as var".$i.", ";
}

$sqlStr .= "to_char(valid, 'YYYY-MM-DD HH24:MI') as dvalid from ".$table ;
$sqlStr .= " WHERE valid >= '".$sqlTS1."' and valid <= '".$sqlTS2 ."' ";
$sqlStr .= " and extract(minute from valid)::int % ".$sampleStr[$sample] ." = 0 ";
$sqlStr .= " and station = '". $stations[0][0] ."' ORDER by valid ASC";

$connection = iemdb("asos1min");

if ($tz == 'UTC'){
	$query1 = "SET TIME ZONE 'GMT'";
	$result = pg_exec($connection, $query1);
}
$rs =  pg_exec($connection, $sqlStr);

pg_close($connection);

$dataA = Array();
$times = Array();

for ($j=0; $j<$num_vars; $j++){
  $dataA[$j] = Array();
}


for( $i=0; $row = pg_fetch_array($rs); $i++){
  $times[$i] = strtotime($row["dvalid"]);
  for ($j=0; $j<$num_vars; $j++){
   $dataA[$j][$i] = $row["var".$j];
  }
} // End of for looper
 

// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example3");
$graph->SetScale("datlin");
$graph->img->SetMargin(40,20,50,100);

$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
//$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);

//$graph->yaxis->scale->ticks->Set(5,1);
//$graph->yaxis->scale->ticks->SetPrecision(0);

$graph->title->Set("Dynamic ASOS Plot for ". $cities[$station]["name"]);
$graph->subtitle->Set("Plot valid between: ".$sqlTS1 ." & ". $sqlTS2 );
$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
//$graph->yaxis->SetTitle("");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid $tz");
$graph->xaxis->SetTitleMargin(70);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

//$ints = $i % 60 ;
//if ($ints > 1)
//$graph->xaxis->SetTextLabelInterval($ints);
$graph->legend->Pos(0.01, 0.01, "right", "top");
$graph->yscale->SetGrace(10);

$colors = Array("red", "blue", "green");

$lp = Array();

for ($j=0;$j<$num_vars;$j++){
  // Create the linear plot
  $lp[$j]=new LinePlot($dataA[$j], $times);
  $lp[$j]->SetColor($colors[$j]);
  $lp[$j]->SetLegend($vars[$j]);

  // Add the plot to the graph
  $graph->Add($lp[$j]);
}

// Display the graph
$fp = "jpgraph_". $station ."_". time() .".png";
$graph->Stroke("/var/webtmp/". $fp);

echo "<p><img src=\"/tmp/". $fp ."\">\n";

?>
