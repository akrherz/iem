<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
	<TITLE>IEM | Current Data</TITLE>
	<META NAME="AUTHOR" CONTENT="Dave Flory">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<link rel="stylesheet" type="text/css" href="/css/mesonet.css">
</HEAD>

<?php
  $product="aviation";
  $current="temperature";
  include("../../include/header2.php");
  include("../../include/header_products.php");
  include("../../include/header_ag.php");

?>

<TABLE class="aviation" >
        <TR><TD>&nbsp;</TD></TR><TR>
        <TR>
        <TD class="shortspacer">&nbsp</TD>
        <TD class="top">
          <TABLE class="subpage">
            <TR><TD><font class="greent12">Temperatures</font></TD></TR>
            <TR><TD>
              <TABLE>
                <TR>
                  <TD class="hlink"><a class="hlink" href="/data/summary/asos_hilo.gif">Yesterday's High/Low</a></TD>
                  <TD class="hlink"><a class="hlink" href="/data/summary/coopAveTemp.gif">Average Hi/Low</a></TD>
                  <TD class="hlink"><a class="hlink" href="/data/summary/coopRecTemp.gif">Record Hi/Low</a></TD>
                </TR>
              </TABLE></TD></TR>
            <TR><TD>&nbsp;</TD></TR>
            <TR><TD><font class="greent12">Current Temperatures</font></TD></TR>
            <TR><TD>
              <UL>
                 <LI><a class="hlink" href="/data/mesonet.gif">Current Mesonet Plot</a></LI>
              </UL></TD></TR>
            <TR><TD>&nbsp;</TD></TR>
            <TR><TD><font class="greent12">Seasonal</font></TD></TR>
            <TR><TD>
               <UL>
                 <LI><div class="left">Minimum temp this fall/winter:
                    &nbsp; &nbsp; <a class="hlink" href="/data/summary/fallLow.gif">Plot</a> or
                    <a class="hlink" href="/data/summary/fallLowC.gif">Contour</a></div></LI>
                 <LI><a  class="hlink" href="/data/summary/mon_mean_T.gif">Current Monthly Mean Temperature</a></LI>
               </UL>
            </TD></TR>
            <TR><TD>&nbsp;</TD></TR>
            <TR><TD><font class="greent12">Soil</font></TD></TR>
            <TR><TD>
              <UL>
                 <LI><a class="hlink" href="/agclimate/daily_pics/soil-hilo-out.gif">Yesterday's Max/Min 4-inch Soil Temperatures</a></LI>
                 <LI><A class="hlink" HREF="/agclimate/daily_pics/4in-temp-out.png">Average 4in Soil Temps</A></LI>
              </UL></TD></TR>
           <TR><TD>&nbsp;</TD></TR>
           <TR><TD><font class="greent12">Indices</font></TD></TR>
           <TR><TD>
             <UL>
               <LI><a class="hlink" href="/data/heat.gif">Heat Index</a></LI>
               <LI><a class="hlink" href="/data/wceq.gif">Wind Chill Index</a></LI>
             </UL>
           </TD></TR>
           <TR><TD>&nbsp;</TD></TR>
           </TABLE>
        </TD></TR>
</TABLE>

<?php include("../../include/footer2.php"); ?>
