<?php 
// A glorious hack to make content coming from twitter/facebook prettier
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/vtec.php";

$v = isset($_GET["vtec"]) ? $_GET["vtec"] : "2012-O-NEW-KBMX-TO-W-0001";
$tokens = preg_split('/-/', $v);
$year = intval($tokens[0]);
$operation = $tokens[1];
$vstatus = $tokens[2];
$wfo4 = $tokens[3];
$wfo = substr($wfo4,1,3);
$phenomena = $tokens[4];
$significance = $tokens[5];
$eventid = intval( $tokens[6] );

// Get the product text
$pgconn = iemdb("postgis");
$table = sprintf("warnings_%s", $year);
pg_prepare($pgconn, 's', "SELECT max(report) as r,
		sumtxt(name::text || ', ') as cnties from warnings_2016 w JOIN ugcs u ".
		"on (w.gid = u.gid) WHERE ".
		"w.wfo = $1 and phenomena = $2 and significance = $3 and
		eventid = $4");
$rs = pg_execute($pgconn, 's', Array($wfo, $phenomena, $significance,
		$eventid));
$row = pg_fetch_assoc($rs, 0);
$report = $row["r"];
$desc = trim($row["cnties"], ', ');

$ogimg = sprintf("https://mesonet.agron.iastate.edu/GIS/vtec_%s.png", $v);
$ogurl = sprintf("https://mesonet.agron.iastate.edu/vtec/f/%s", $v);
$ogtitle = sprintf("%s %s %s %s", $wfo, $vtec_phenomena[$phenomena],
		$vtec_significance[$significance], $eventid);

?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="refresh" content="0; /vtec/#<?php echo $v; ?>"> 
<title><?php echo $ogtitle; ?></title>
<meta property="og:title" content="<?php echo $ogtitle; ?>">
<meta property="og:description" content="<?php echo $desc; ?>">
<meta property="og:image" content="<?php echo $ogimg; ?>">
<meta property="og:url" content="<?php echo $ogurl; ?>">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@akrherz">
<meta name="og:image:width" content="600">
<meta name="og:image:height" content="315">
<meta name="og:site_name" content="Iowa Environmental Mesonet">
<meta name="twitter:image:alt" content="Visualization of the VTEC Product">
</head>
<body>
<pre>
<?php echo $report; ?>
</pre>

</body>
</html>
