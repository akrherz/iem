<?php
/* 
 * This is an Extjs application that allows historical and current viewing of
 * webcam images.
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 9);
require_once "../../include/myview.php";
$t = new MyView();
 require_once "../../include/iemprop.php";
 $camera_refresh = get_iemprop("webcam.interval");
$t->headextra = <<<EOF
<link rel="stylesheet" type="text/css" href="https://extjs.cachefly.net/ext/gpl/5.0.0/build/packages/ext-theme-neptune/build/resources/ext-theme-neptune-all.css"/>
<script type="text/javascript" src="https://extjs.cachefly.net/ext/gpl/5.0.0/build/ext-all.js"></script>
<script>
Ext.namespace('cfg');
cfg.refreshint = ${camera_refresh}000;
cfg.header = 'iem-header';
cfg.headerHeight = 60;
cfg.jsonSource = '/json/webcams.php';
</script>
  <script type='text/javascript' src='webcam-static.js?v=7'></script>
<style>
.webimage {
  height: 240px;
  width : 320px;
}
.thumb-wrap{
    float: left;
    margin: 1px;
    margin-right: 0;
    padding: 5px;
    width: 325px;
}
.x-view-over{
    border:1px solid #dddddd;
    padding: 4px;
}

</style>
EOF;
$t->title = "Webcams";
$t->content = <<<EOF
<div id="main">
</div>
<div id="iem-header">
<a href="/">IEM Homepage</a>
</div>
<div id="iem-footer"></div>
<div id="help" class="x-hidden">
<h3 style="margin: 10px;">Web Camera Interactive Viewer</h3>

<p>This application provides an interactive view of current and historical
web camera imagery. Click on the 'Real Time' button above to switch the
application into 'Archived Mode'.  You can then select the time of interest
and the application will automatically update to show you the images. The IEM has archived images every 5 minutes, but may have an image every minute during active weather.</p>
<br /><br />
<strong>Cool Archived Images:</strong><br />
<ul style="margin-left: 5px;">
 <li><a href="javascript: app.appSetTime('KCCI-200406120132')">11 Jun 2004 - 7:32 PM, Webster City Tornado</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200505270115')">26 May 2005 - 7:15 PM, Pella Double Rainbow</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200506090255')">8 Jun 2005 - 8:55 PM, All sorts of colours</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200509081730')">8 Sep 2005 - 12:30 PM, Blurry shot of Ames Tornado</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200511122238')">12 Nov 2005 - 4:38 PM, Woodward tornado from Madrid</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200511122300')">12 Nov 2005 - 5:00 PM, Ames tornado</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200607172150')">17 Jul 2006 - 4:50 PM, Tama possible brief tornado</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200710022256')">2 Oct 2007 - 5:56 PM, Twin Cedars possible tornado</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200808310120')">30 Aug 2008 - 8:20 PM, Interesting Sunset Halos</a></li>
</ul>

</div>
EOF;
$t->render('app.phtml');
?>
