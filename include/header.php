<?php
  include("$rootpath/include/catch_phrase.php");
  srand ((float) microtime() * 10000000);
  $t = array_rand($phrases);
  $phrase = $phrases[$t];

?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" <?php if (isset($GOOGLEKEYS)){echo "xmlns:v=\"urn:schemas-microsoft-com:vml\"";} if (isset($HTMLEXTRA)){ echo $HTMLEXTRA; }?>>
<head>
 <title><?php echo isset($TITLE) ? $TITLE: "Iowa Environmental Mesonet"; ?></title>
 <link rel="stylesheet" type="text/css" media="screen" href="<?php echo $rooturl; ?>/css/main.css?v=3" />
 <link rel="stylesheet" type="text/css" media="print" href="<?php echo $rooturl; ?>/css/print.css?v=3" />
 <?php if (isset($REFRESH)){ echo $REFRESH; } ?>
 <?php if (isset($HEADEXTRA)){ echo $HEADEXTRA;} ?>
</head>
<body <?php if (isset($BODYEXTRA)){ echo $BODYEXTRA;} ?>>
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
    "browse" => Array("title" => "Browse data/", "url" => "/archive/data/"),
    "birthday" => Array("title" => "Birthday Weather", "url" => "/onsite/birthday/"),
    "cases" => Array("title" => "Cases", "url" => "/cases/"),
    "mos" => Array("title" => "MOS", "url" => "/mos/"),
 ),
 "current" => Array(
    "base" => Array("title" => "Current", "url" => "/current/"),
    "advanced" => Array("title" => "Advanced Products", "url" => "/current/misc.phtml"),
    "sort" => Array("title" => "Sortable Currents", "url" => "/my/current.phtml"),
    "surface" => Array("title" => "Surface Data", "url" => "/current/"),
    "radar" => Array("title" => "RADAR & Satellite", "url" => "/current/radar.phtml"),
    "placefiles" => Array("title" => "GR Placefiles", "url" => "/request/grx/"),
    "afos" => Array("title" => "NWS Text", "url" => "/wx/afos/"),
 ),
 "climatology" => Array(
    "base" => Array("title" => "Climatology", "url" => "/climate/"),
    "main" => Array("title" => "Mainpage", "url" => "/climate/"),
    "climodat" => Array("title" => "Climodat", "url" => "/climodat/"),
    "today" => Array("title" => "Today", "url" => "/climate/today.phtml"),
    "yesterday" => Array("title" => "Yesterday", "url" => "/climate/yesterday.phtml"),
    "week" => Array("title" => "Week", "url" => "/climate/week.phtml"),
    "month" => Array("title" => "Month", "url" => "/climate/month.phtml"),
    "year" => Array("title" => "Year", "url" => "/climate/year.phtml"),
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
 ),
 "networks" => Array(
    "base" => Array("title" => "IEM Networks", "url" => "/"),
    "asos" => Array("title" => "ASOS", "url" => "/ASOS/"),
    "awos" => Array("title" => "AWOS", "url" => "/AWOS/"),
    "coop" => Array("title" => "NWS COOP", "url" => "/COOP/"),
    "dcp" => Array("title" => "DCP", "url" => "/DCP/"),
    "agclimate" => Array("title" => "ISU AG", "url" => "/agclimate/"),
    "flux" => Array("title" => "NSTL Flux", "url" => "/nstl_flux/"),
    "rwis" => Array("title" => "RWIS", "url" => "/RWIS/"),
    "scan" => Array("title" => "SCAN", "url" => "/scan/"),
    "schoolnet" => Array("title" => "SchoolNet", "url" => "/schoolnet/"),
    "other" => Array("title" => "Other", "url" => "/other/"),
 ),
 "gis" => Array(
    "base" => Array("title" => "GIS", "url" => "/GIS/"),
    "browse" => Array("title" => "Browse Data", "url" => "/data/gis/"),
    "nexrad" => Array("title" => "NEXRAD Data", "url" => "/docs/nexrad_composites/"),
    "ogc" => Array("title" => "OGC Webservices", "url" => "/ogc/"),
    "rainfall" => Array("title" => "Rainfall Data", "url" => "/rainfall/"),
    "satellite" => Array("title" => "Satellite Data", "url" => "/GIS/goes.phtml"),
    "software" => Array("title" => "Software", "url" => "/GIS/software.php"),
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
    "river" => Array("title" => "River Summary", "url" => "/river/wfo.phtml"),
    "watch" => Array("title" => "SPC Watches", "url" => "/GIS/apps/rview/watch.phtml"),
    "vtec" => Array("title" => "VTEC Browser", "url" => "/vtec/"),
 ),
 "webcam" => Array(
    "base" => Array("title" => "Web Cams", "url" => "/current/camera.phtml"),
    "still" => Array("title" => "Still Images", "url" => "/current/camera.phtml"),
    "viewer" => Array("title" => "Hi-res + Live", "url" => "/current/viewer.phtml"),
    "loop" => Array("title" => "Loops", "url" => "/current/bloop.phtml"),
    "lapse" => Array("title" => "Recent Movies", "url" => "/current/camlapse/"),
    "cool" => Array("title" => "Cool Lapses", "url" => "/cool/"),
 ),
);
$THISPAGE = isset($THISPAGE) ? $THISPAGE : "networks-base";
$ar = split("-", $THISPAGE);
if (sizeof($ar) == 1) $ar[1] = "";
echo "<div id=\"iem_nav\"><ul>\n";
$b = "";
while( list($idx, $page) = each($_pages) )
{
  echo sprintf("<li%s><a href=\"%s\">%s</a></li>", 
      ($ar[0] == $idx) ? " class=\"selected\"" : " ",
      $rooturl . $page["base"]["url"], $page["base"]["title"]);
  if ($ar[0] == $idx)
  {
    $b .= "<div id=\"iem_subnav\"><ul>\n";
    while( list($idx2, $page2) = each($page) )
    {
       if ($idx2 == "base") continue;
       $b .= sprintf("<li%s><a href=\"%s\">%s</a></li>", 
         ($ar[1] == $idx2) ? " class=\"selected\"" : " ",
          $rooturl . $page[$idx2]["url"], 
     ($ar[1] == $idx2) ? "[ ". $page[$idx2]["title"] ." ]": $page[$idx2]["title"] );
    }
    $b .= "</ul></div>\n";
  }
}
echo "</ul></div> $b";
?>

 
</div><!-- End of iem-header -->
<?php if (! isset($NOCONTENT)) echo "<div id=\"iem-content\">"; ?>
