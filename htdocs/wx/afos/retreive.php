<?php
$conn = pg_connect("dbname=afos host=mtarchive.geol.iastate.edu user=nobody");

$pil = strtoupper($_POST["pil"]);
$cnt = $_POST["cnt"];

$sql = "SELECT * from current WHERE pil = '$pil'
   ORDER by entered DESC LIMIT $cnt";
$result = pg_exec($conn, $sql);

$row = pg_fetch_array($result,0);

echo "<pre>". $row["data"] ."</pre>";

?>
