<?php
/* This is gonna be painful */
include("../../config/settings.inc.php");
 include("$rootpath/include/constants.php");
$HEADEXTRA = "
  <link rel='stylesheet' type='text/css' href='../ext-3.0-rc2/resources/css/ext-all.css'/>
  <script type='text/javascript' src='../ext-3.0-rc2/adapter/ext/ext-base.js'></script>
  <script type='text/javascript' src='../ext-3.0-rc2/ext-all.js'></script>
<script>
Ext.namespace('cfg');
cfg.refreshint = ${camera_refresh}000;
cfg.header = 'iem-header';
cfg.headerHeight = 150;
cfg.jsonSource = '../json/webcams.php';
</script>
  <script type='text/javascript' src='webcam-static.js?v=1'></script>
<style>
.thumb-wrap{
    float: left;
    margin: 1px;
    margin-right: 0;
    padding: 5px;
}
.x-view-over{
    border:1px solid #dddddd;
    padding: 4px;
}

</style>";
$NOCONTENT = 1;
$TITLE = "IEM Webcams";
$THISPAGE = "webcam-still";
include("$rootpath/include/header.php");
?>
<div id="main">
</div>

<div id="help" class="x-hidden">
<h3 style="margin: 10px;">Web Camera Interactive Viewer</h3>

<p>This application provides an interactive view of current and historical
web camera imagery. Click on the 'Real Time' button above to switch the
application into 'Archived Mode'.  You can then select the time of interest
and the application will automatically update to show you the images. The IEM has archived images every 5 minutes, but may have an image every minute during active weather.</p>
<br /><br />
<strong>Cool Archived Images:</strong><br />
<ul style="margin-left: 5px;">
 <li><a href="javascript: app.appSetTime('KCCI-200406111932')">11 Jun 2004 - 7:32 PM, Webster City Tornado</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200505261915')">26 May 2005 - 7:15 PM, Pella Double Rainbow</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200506082055')">8 Jun 2005 - 8:55 PM, All sorts of colours</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200509081230')">8 Sep 2005 - 12:30 PM, Blurry shot of Ames Tornado</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200511121638')">12 Nov 2005 - 4:38 PM, Woodward tornado from Madrid</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200511121700')">12 Nov 2005 - 5:00 PM, Ames tornado</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200607171650')">17 Jul 2006 - 4:50 PM, Tama possible brief tornado</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200710021756')">2 Oct 2007 - 5:56 PM, Twin Cedars possible tornado</a></li>
 <li><a href="javascript: app.appSetTime('KCCI-200808302020')">30 Aug 2008 - 8:20 PM, Interesting Sunset Halos</a></li>
</ul>

</div>

</body>
</html>
