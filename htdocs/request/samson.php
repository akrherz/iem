<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd"> 
<HTML>
<HEAD>
	<TITLE>IEM | Request SAMSON data</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/main.css">
</HEAD>

<?php 
	$title = "IEM | Request SAMSON data";
	include("../include/header.php"); 
?>

<TR>

<?php include("../include/side.html"); ?>
<?php include("../include/imagemaps.php"); ?>

<TD width="450" valign="top">
<P>Back to <a href="/request">Request Other Data</a>.

<P>By selecting a station below, you can download the entire archive of data for a given 
station in SAMSON format.

<BR><BR>

<?php
 if ( strlen($rwis) > 0) {
?>
<P><a href="samson.php">Different ASOS/AWOS Location</a>
<BR><BR>

<?php  echo print_rwis("/cgi-bin/request/samson.py?station"); ?>

<?php
}else {
?>
<P>Switch to<a href="samson.php?rwis=yes">RWIS</a> stations.

<?php  echo print_asos("/cgi-bin/request/samson.py?station"); ?>



<?php 
	}
?>



</TD></TR>

<?php include("../include/footer.html"); ?>
