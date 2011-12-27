<?php 
include("../../../config/settings.inc.php");
define("IEM_APPID", 55);
include("$rootpath/include/database.inc.php");
include("$rootpath/include/feature.php");
$day = isset($_GET["day"]) ? substr($_GET["day"],0,10) : null;
$offset = isset($_GET["offset"]) ? $_GET["offset"] : 0;
if ($day == null){
	$day = Date("Y-m-d");
	$offset = -1;
}

$dbconn = iemdb("mesosite");
$rs = pg_prepare($dbconn, "yesterday", "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE valid < $1 ORDER by valid DESC limit 1");
$rs = pg_prepare($dbconn, "today", "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE date(valid) = $1");
$rs = pg_prepare($dbconn, "tomorrow", "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE valid > ($1::date + '1 day'::interval) 
              ORDER by valid ASC limit 1");

$q = "today";
if ($offset == "-1"){ $q = "yesterday"; }
else if ($offset == "+1") {$q = "tomorrow";}
$result = pg_execute($dbconn, $q, Array($day));

if (pg_num_rows($result) == 0){ die("Feature Not Found"); }

$row = pg_fetch_array($result,0);
$valid = strtotime( $row["valid"] );
$fmt = "gif";
if ($valid > strtotime("2010-02-19")){ $fmt = "png"; }

if ($row["fbid"] == null){
	$row["fbid"] = $valid;
}

$day = $row["d"];
$thumb = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s_s.%s", $row["imageref"], $fmt);
$big = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s.%s", $row["imageref"], $fmt);

$TITLE = "IEM Past Feature $day - ". $row["title"]; 
$THISPAGE = "iem-feature";
include("$rootpath/include/header.php"); 

?>
<a class="button down" href="cat.php?day=<?php echo $day; ?>&offset=-1">Previous Feature by Date</a> 
<strong>IEM Daily Feature for <?php echo $day; ?></strong>
<a class="button up" href="cat.php?day=<?php echo $day; ?>&offset=+1">Next Feature by Date</a>
<hr />
<!-- Begin Feature Display -->
<div style="width: 640px;">

<table cellpadding="2" cellspacing="0" border="1">
<tr><td>Title:</td><td><strong><?php echo $row["title"]; ?></strong></td></tr>
<tr><td>Posted:</td><td><?php echo $row["webdate"]; ?></td></tr>
</table>

<div style="float: left; padding: 5px; ">
<a href="<?php echo $big; ?>"><img src="<?php echo $thumb; ?>" style="margin: 5px; border:0px;"></a>
<br /><a href="<?php echo $big; ?>">View larger image</a>
<br /><?php echo $row["caption"]; ?>
</div>
<?php
  echo "<br><div class='story'>". $row["story"] ;
  if ($row["voting"] == 't' && (intval($row["good"]) > 0 || intval($row["bad"]) > 0))
  {
    echo "<br /><br /><b>Voting:</b><br />Good = ". $row["good"] ." <br />Bad = ". $row["bad"] ;
  }
  echo "<br />". printTags(explode(",", $row["tags"]));
?>
</div>
<div id="fb-root"></div>
<script src="http://connect.facebook.net/en_US/all.js#appId=196492870363354&amp;xfbml=1"></script>
<fb:comments send_notification_uid="16922938" 
 callback="<?php echo $rooturl; ?>/fbcb.php" title="<?php echo $row["title"]; ?>" 
 href="<?php echo $rooturl; ?>/onsite/features/cat.php?day=<?php echo $day; ?>" 
 xid="<?php echo $row["fbid"]; ?>" numposts="6" width="600"></fb:comments>

<?php include("$rootpath/include/footer.php"); ?>
