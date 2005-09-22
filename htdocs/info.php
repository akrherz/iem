<?php
include("../config/settings.inc.php");
$TITLE = "IEM | Information";
include("$rootpath/include/header.php"); ?>


<h3 class="heading">Information/Documents</h3><p>

<div class="text">
<table border=0 width="100%"><tr><td valign="top">

<h3 class="subtitle">Quick Links:</h3></p>
<ul>
<li><a href="/info/iem.php">IEM Info/Background</a></li>
<li><a href="/info/members.php">IEM Partners</a></li>
<li><a href="/info/links.php">Links</a></li>
<li><a href="/sites/networks.php">Network Tables</a></li>
<li><a href="/info/variables.phtml">Variables Collected</a></li></ul>

<p>Information about requesting a <a href="/request/ldm.php">real-time data feed</a>
<p>
<h3 class="subtitle">Station Locations: (graphical)</h3>
<ul>
	<li><a href="images/asosLocs.jpg">ASOS Locations</a></li>
	<li><a href="images/awosLocs.jpg">AWOS Locations</a></li>
	<li><a href="images/rwis_sites.gif">RWIS Locations</a></li>
	<li><a href="images/coop_sites.gif">COOP Locations</a></li>
	<li><a href="images/isuag_sites.gif">ISU Agclimate Locations</a></li>
</ul>

</td><td width="50%" valign="top">

<h3 class="subtitle">IEM Projects:</h3>
<ul>
 <li><a href="/projects/iembot/">iembot</a>
  <br />A Jabber chat bot relaying NWS warnings.</li>
</ul>

<h3 class="subtitle">IEM Server Information:</h3>
<ul>
	<li><a href="/info/software.php">Software Utilized</a></li>
	<li><a href="/ml/">Mailing Lists</a></li>
</ul>

<h3 class="subtitle">Documents:</h3>
<ul>
        <li><B>IEM Meeting Agenda:</B> (<a href="/pubs/iem-agenda.doc">DOC</a> )
          <BR><i>Author:</i> Dennis Todey &nbsp; &nbsp; 10 May 2001
        </li>

        <li><B>Data Acquisition: (WIP)</B> (<a href="/pubs/dataSources.pdf">PDF</a> )
         <BR><i>Author:</i> Daryl Herzmann &nbsp; &nbsp; 05 Oct 2001
        </li>

        <li><B>RWIS Data Inventory:</B> (<a href="/pubs/RWISinv.pdf">PDF</a> )
         <BR><i>Author:</i> Daryl Herzmann &nbsp; &nbsp; 1 Jan 2002
        </li>
</ul>

<h3 class="subtitle">Papers/Presentations</h3>
<ul>
  <li><a href="/pubs/seniorthesis/">ISU Senior Thesis Presentations</a></li>
  <li><a href="/present/">IEM Presentation Archive</a></li>
</ul>

</td></tr></table></div>

<?php include("$rootpath/include/footer.php"); ?>
