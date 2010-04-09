<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$conn = iemdb("postgis");

$v = isset($_GET["vtec"]) ? $_GET["vtec"] : "2008-O-NEW-KJAX-TO-W-0048";
$tokens = split("-", $v);
$year = $tokens[0];
$operation = $tokens[1];
$vstatus = $tokens[2];
$wfo4 = $tokens[3];
$wfo = substr($wfo4,1,3);
$phenomena = $tokens[4];
$significance = $tokens[5];
$eventid = intval( $tokens[6] );

/* Get the product text */
$rs = pg_prepare($conn, "SELECT" , "SELECT replace(report,'\001','') as report,
        replace(svs,'\001','') as svs
        from warnings_$year w WHERE w.wfo = $1 and 
        w.phenomena = $2 and w.eventid = $3 and 
        w.significance = $4 ORDER by length(svs) DESC LIMIT 1");

$rs = pg_execute($conn, "SELECT", Array($wfo, $phenomena, $eventid, $significance));
$txtdata = "";
for( $i=0; $row  = @pg_fetch_array($rs,$i); $i++){
  $tokens = @explode('__', $row["svs"]);
  while (list($key,$val) = each($tokens))
  {
    if ($val == "") continue;
    $txtdata .= $val ."<hr />";
  }
  $txtdata .= $row["report"];
}

?>
<html>
<head>
 <title>VTEC Browser for Mobile</title>
</head>
<body>
<h3>VTEC Browser for Mobile</h3>

<img src="<?php echo $rooturl; ?>/GIS/radmap.php?layers[]=uscounties&layers[]=sbw&layers[]=nexrad&width=300&height=300&vtec=<?php echo str_replace('-', '.', $v); ?>" />

<pre>
<?php echo $txtdata; ?>
</pre>
</body>
</html>
