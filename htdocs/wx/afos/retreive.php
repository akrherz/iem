<?php
$conn = pg_connect("dbname=afos host=mtarchive.geol.iastate.edu user=nobody");

$pil = strtoupper($_POST["pil"]);
$cnt = $_POST["cnt"];

$rs = pg_prepare($conn, "SELECT", "SELECT * from current WHERE pil = $1
                         ORDER by entered DESC LIMIT $2");

$rs = pg_execute($conn, "SELECT", Array($pil, $cnt));

if (pg_numrows($rs) == 0){
 echo "<h3>No entries found for ${pil}</h3>";
}

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{ 
  echo "<pre>". $row["data"] ."</pre><hr />";
}

?>
