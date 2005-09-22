<?php
// Print out all events for this year!

$c = pg_connect("10.10.10.20", 5432, "wepp");
$q = "select * from results_by_twp WHERE model_twp = '$twp' ORDER by valid ASC";
$rs = pg_exec($c, $q);
?>
<table border=1>
<tr>
  <th rowspan=2>Date:</th>
  <th rowspan=2># Runs:</th>
  <th colspan=3>Rainfall [in]</th> 
  <th colspan=3>Soil Loss [ton/acre]</th> 
  <th colspan=3>Runoff [ton/acre]</th> 
</tr>
<tr>
  <th>Min:</th><th>Avg:</th><th>Max:</th>
  <th>Min:</th><th>Avg:</th><th>Max:</th>
  <th>Min:</th><th>Avg:</th><th>Max:</th>
</tr>
<?php
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  $ts = strtotime($row["valid"]);
  $url = "township.phtml?twp=$twp&". strftime("year=%Y&month=%m&day=%d", $ts);
  echo "<tr><td><a href=\"$url\">". $row["valid"] ."</a></td>
    <td>". $row["run_points"] ."</td>
    <td>". round($row["min_precip"] / 25.4, 2)."</td>
    <td>". round($row["avg_precip"] / 25.4, 2) ."</td>
    <td>". round($row["max_precip"] / 25.4, 2) ."</td>
    <td>". round($row["min_loss"] * 4.463, 2) ."</td>
    <td>". round($row["avg_loss"] * 4.463, 2) ."</td>
    <td>". round($row["max_loss"] * 4.463, 2)."</td>
    <td>". round($row["min_runoff"] / 25.4, 2) ."</td>
    <td>". round($row["avg_runoff"] / 25.4, 2) ."</td>
    <td>". round($row["max_runoff"] / 25.4, 2) ."</td>
  </tr>";
}
echo "</table>";
?>
