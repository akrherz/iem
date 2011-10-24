<?php
  include("$rootpath/include/catch_phrase.php");
  srand ((float) microtime() * 10000000);
  $t = array_rand($phrases);
  $phrase = $phrases[$t];

?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" <?php if (isset($GOOGLEKEYS)){echo "xmlns:v=\"urn:schemas-microsoft-com:vml\"";} if (isset($HTMLEXTRA)){ echo $HTMLEXTRA; }?>>
<head>
 <title><?php echo isset($TITLE) ? $TITLE: "Iowa Environmental Mesonet"; ?></title>
 <link rel="stylesheet" type="text/css" media="screen" href="<?php echo $rooturl; ?>/css/main.css?v=5" />
 <link rel="stylesheet" type="text/css" media="print" href="<?php echo $rooturl; ?>/css/print.css?v=4" />
 <?php if (isset($REFRESH)){ echo $REFRESH; } ?>
 <?php if (isset($HEADEXTRA)){ echo $HEADEXTRA;} ?>
<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-784549-2']);
_gaq.push(['_trackPageview']);
(function() {
var ga = document.createElement('script');
ga.src = ('https:' == document.location.protocol ?
    'https://ssl' : 'http://www') +
    '.google-analytics.com/ga.js';
ga.setAttribute('async', 'true');
document.documentElement.firstChild.appendChild(ga);
})();
</script>
<script type="text/javascript" src="<?php echo $rooturl; ?>/js/p7exp.js"></script>
<!--[if lte IE 7]>
<style>
#menuwrapper, #p7menubar ul a {height: 1%;}
a:active {width: auto;}
</style>
<![endif]-->
</head>
</head>
<body <?php if (isset($BODYEXTRA)){ echo $BODYEXTRA;} ?> onLoad="P7_ExpMenu()">
<?php if (! isset($NOCONTENT)) echo "<div id=\"iem-main\">"; ?>
<div id="iem-header">
<?php include("$rootpath/include/webring.html"); ?>
<div id="iem_header_logo">
<a href="<?php echo $rooturl; ?>/"><img src="<?php echo $rooturl; ?>/images/logo_small.gif" alt="IEM" /></a>
</div>                                                                         
<div id="iem-header-title">
<h3>Iowa Environmental Mesonet</h3>
<h4>Iowa State University Department of Agronomy</h4>
</div>                                                
<div id="iem-header-items">
<i><?php echo $phrase; ?></i>
</div>
<?php
$_pages = Array(
 "archive" => Array(
    "base" => Array("title" => "Archive", "url" => "/archive/"),
    "schema" => Array("title" => "Archive Schema", "url" => "/archive/schema.php"),
    "browse" => Array("title" => "Browse data/", "url" => "/archive/data/"),
    "birthday" => Array("title" => "Birthday Weather", "url" => "/onsite/birthday/"),
    "hrain" => Array("title" => "Hourly Precip", "url" => "/rainfall/obhour.phtml"),
    "iemre" => Array("title" => "IEM Reanalysis", "url" => "/iemre/"),
    "cases" => Array("title" => "Interesting Cases", "url" => "/cases/"),
	"mos" => Array("title" => "Model Output Statistics", "url" => "/mos/"),
    "tm" => Array("title" => "Time Machine", "url" => "/timemachine/"),
 ),
  "climatology" => Array(
    "base" => Array("title" => "Climate", "url" => "/climate/"),
	"extremes" => Array("title" => "Daily Climatology", "url" => "/COOP/extremes.php"),
    "main" => Array("title" => "Mainpage", "url" => "/climate/"),
    "climodat" => Array("title" => "Climodat", "url" => "/climodat/"),
    "drought" => Array("title" => "Drought", "url" => "/dm/"),
    "today" => Array("title" => "Today", "url" => "/climate/today.phtml"),
    "yesterday" => Array("title" => "Yesterday", "url" => "/climate/yesterday.phtml"),
    "week" => Array("title" => "Week", "url" => "/climate/week.phtml"),
    "month" => Array("title" => "Month", "url" => "/climate/month.phtml"),
    "gs" => Array("title" => "Growing Season", "url" => "/climate/gs.phtml"),
    "year" => Array("title" => "Year", "url" => "/climate/year.phtml"),
 ),
 "current" => Array(
    "base" => Array("title" => "Current", "url" => "/current/"),
    "products" => Array("title" => "Products", "url" => "/current/"),
    "sort" => Array("title" => "Sortable Currents", "url" => "/my/current.phtml"),
    "month" => Array("title" => "Month", "url" => "/current/month.phtml"),
    "gs" => Array("title" => "Growing Season", "url" => "/current/gs.phtml"),
    "year" => Array("title" => "Year", "url" => "/current/year.phtml"),
    "radar" => Array("title" => "RADAR & Satellite", "url" => "/current/radar.phtml"),
    "placefiles" => Array("title" => "GR Placefiles", "url" => "/request/grx/"),
    "afos" => Array("title" => "NWS Text", "url" => "/wx/afos/"),
 ),
 "iem" => Array(
    "base" => Array("title" => "Info", "url" => "/sites/locate.php"),
    "feature" => Array("title" => "Daily Features", "url" => "/onsite/features/past.php"),
    "sites" => Array("title" => "IEM Sites", "url" => "/sites/locate.php"),
    "info" => Array("title" => "Info", "url" => "/info.php"),
    "links" => Array("title" => "Links", "url" => "/info/links.php"),
    "mailman" => Array("title" => "Mail Lists", "url" => "/mailman/listinfo/"),
    "news" => Array("title" => "News", "url" => "/onsite/news.phtml"),
    "networks" => Array("title" => "Network Tables", "url" => "/sites/networks.php"),
    "present" => Array("title" => "Presentations", "url" => "/present/"),
    "qc" => Array("title" => "Quality Control", "url" => "/QC/"),
    "variables" => Array("title" => "Variables", "url" => "/info/variables.phtml"),
 ),
  "gis" => Array(
    "base" => Array("title" => "GIS", "url" => "/GIS/"),
    "browse" => Array("title" => "Browse Data", "url" => "/data/gis/"),
    "nexrad" => Array("title" => "NEXRAD Data", "url" => "/docs/nexrad_composites/"),
    "ogc" => Array("title" => "OGC Webservices", "url" => "/ogc/"),
    "rainfall" => Array("title" => "Rainfall Data", "url" => "/rainfall/"),
    "radmap" => Array("title" => "RadMap API", "url" => "/GIS/radmap_api.phtml"),
    "satellite" => Array("title" => "Satellite Data", "url" => "/GIS/goes.phtml"),
    "software" => Array("title" => "Software", "url" => "/GIS/software.php"),
 ),
 "networks" => Array(
    "base" => Array("title" => "Networks", "url" => "/"),
    "asos" => Array("title" => "ASOS", "url" => "/ASOS/"),
    "awos" => Array("title" => "AWOS", "url" => "/AWOS/"),
    "coop" => Array("title" => "NWS COOP", "url" => "/COOP/"),
    "dcp" => Array("title" => "DCP", "url" => "/DCP/"),
    "agclimate" => Array("title" => "ISU AG", "url" => "/agclimate/"),
    "flux" => Array("title" => "NLAE Flux", "url" => "/nstl_flux/"),
    "rwis" => Array("title" => "RWIS", "url" => "/RWIS/"),
    "scan" => Array("title" => "SCAN", "url" => "/scan/"),
    "schoolnet" => Array("title" => "SchoolNet", "url" => "/schoolnet/"),
    "other" => Array("title" => "Other", "url" => "/other/"),
 ),
 "roads" => Array(
    "base" => Array("title" => "Roads", "url" => "/roads/"),
    "main" => Array("title" => "Mainpage", "url" => "/roads/"),
    "gis" => Array("title" => "GIS Products", "url" => "/roads/gis.phtml"),
    "history" => Array("title" => "Historical", "url" => "/roads/history.phtml"),
    "maps" => Array("title" => "Interactive Map", "url" => "/roads/maps.phtml"),
    "sort" => Array("title" => "Sortable Text", "url" => "/roads/rc.phtml"),
 ),
 "severe" => Array(
    "base" => Array("title" => "Severe Weather", "url" => "/current/severe.phtml"),
    "main" => Array("title" => "Mainpage", "url" => "/current/severe.phtml"),
    "cow" => Array("title" => "IEM Cow", "url" => "/cow/"),
    "iembot" => Array("title" => "iembot", "url" => "/projects/iembot/"),
    "interact" => Array("title" => "Interact Radar", "url" => "/GIS/apps/rview/warnings.phtml"),
    "lsr" => Array("title" => "LSR App", "url" => "/lsr/"),
    "river" => Array("title" => "River Summary", "url" => "/river/"),
    "watch" => Array("title" => "SPC Watches", "url" => "/GIS/apps/rview/watch.phtml"),
    "vtec" => Array("title" => "VTEC Browser", "url" => "/vtec/"),
 ),
 "webcam" => Array(
    "base" => Array("title" => "Web Cams", "url" => "/current/webcam.php"),
    "still" => Array("title" => "Still Images", "url" => "/current/webcam.php"),
    "viewer" => Array("title" => "Hi-res + Live", "url" => "/current/viewer.phtml"),
    "loop" => Array("title" => "Loops", "url" => "/current/bloop.phtml"),
    "lapse" => Array("title" => "Recent Movies", "url" => "/current/camlapse/"),
    "cool" => Array("title" => "Cool Lapses", "url" => "/cool/"),
 ),
);
$THISPAGE = isset($THISPAGE) ? $THISPAGE : "xxx-xxx";
$ar = split("-", $THISPAGE);
if (sizeof($ar) == 1) $ar[1] = "";
echo "<div id=\"menuwrapper\"><ul id=\"p7menubar\">\n";
/* Look for related IEM Apps */
if (defined('IEM_APPID')){
	include_once("$rootpath/include/database.inc.php");
	$_mesosite = iemdb("mesosite");
	pg_prepare($_mesosite, "_SELECTOR_", "SELECT * from iemapps where appid in 
		(SELECT appid from iemapps_tags WHERE tag in (SELECT tag from iemapps_tags where appid = $1)
		and appid != $1) ORDER by name ASC");
	$rs = pg_execute($_mesosite, "_SELECTOR_", Array(IEM_APPID));
	if (pg_numrows($rs) > 0){
		echo "<li><a class=\"trigger\" href=\"#\"><img src=\"". $rooturl ."/images/star.png\" border=\"0\" alt=\"Related\" height=\"15\" style=\"margin-top: -3px; margin-right: 3px;\">Related</a>";
		echo "<ul>\n";
		for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
			$url = $rooturl . $row["url"];
			if (substr($row["url"],0,1) == "h"){
				$url = $row["url"];
			}
			echo sprintf("<li><a href=\"%s\">%s</a></li>", 
         		$url,  $row["name"] );
		}
		echo "</ul></li>\n";
	}
	pg_close($_mesosite);
}
while( list($idx, $page) = each($_pages) )
{
  echo sprintf("<li><a class=\"%s\" href=\"%s\">%s</a>", 
      ($ar[0] == $idx) ? "atrigger" : "trigger",
      $rooturl . $page["base"]["url"], $page["base"]["title"]);

    echo "<ul>\n";
    while( list($idx2, $page2) = each($page) )
    {
       if ($idx2 == "base") continue;
       echo sprintf("<li><a%s href=\"%s\">%s</a></li>", 
         ($ar[1] == $idx2 && $ar[0] == $idx) ? " class=\"alink\"" : "",
          $rooturl . $page[$idx2]["url"],  $page[$idx2]["title"] );
    }
    echo "</ul></li>\n";
}

echo "</ul><br class=\"clearit\"></div>";
?>
</div><!-- End of iem-header -->
<?php if (! isset($NOCONTENT)) echo "<div id=\"iem-content\">"; ?>
