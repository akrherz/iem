<?php
include("../../config/settings.inc.php");
$TITLE = "IEM | NWS Related Information";
$THISPAGE = "iem-info";
include("$rootpath/include/header.php"); ?>

<h3 class="heading">IEM Data for NWS Users</h3><p>

<div class="warning">Please <a href="<?php echo $rooturl; ?>/info/contacts.php">suggest</a> features for this page.  We are looking to collect all relevant
IEM provided archives/applications of NWS data.</div>

<h4>Model Data</h4>
<ul>
 <li><a href="../mos/">Model Output Statistics</a>
 <br />Archive of MOS back to 3 May 2007.</li>
</ul>

<h4>Storm Based Warnings</h4>
<ul>
 <li><a href="../cow/">IEM Cow</a>
  <br />Interactive Storm Based Warning verification app</li>
 <li><a href="../request/gis/watchwarn.phtml">GIS Shapefiles</a>
  <br />of archived Storm Based Warning polygons.</li>
</ul>

<h4>Text Product Archives</h4>
<ul>
 <li><a href="../wx/afos/">AFOS Product Viewer</a>
  <br />Web based version of TextDB.</li>
 <li><a href="../wx/afos/list.phtml">View Products by WFO by Date</a>
  <br />View quick listings of issued products by forecast office and by 
    date.</li>
</ul>

<?php include("$rootpath/include/footer.php"); ?>
