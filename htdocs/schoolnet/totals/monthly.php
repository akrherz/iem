<?php include('../switchtv.php'); ?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
	<TITLE>IEM | Monthly Totals</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/mesonet.css">
</script>
</HEAD>

<?php 
  include("../../include/header2.php"); 
  include("../../include/snetLoc.php"); 
?>

<b>Nav:</b><a href="/schoolnet">School Net</a> <b> > </b> Monthly Totals

<p class="intro">A demo application showing a monthly data report...</p>

<table>

<?php
 $c0 = pg_connect('db1.mesonet.agron.iastate.edu', 5432, 'snet');
 $q0 = "SELECT * from t2002_daily WHERE station = 'SKCI4' and extract(month
  from valid) = 10 ORDER by valid";
 $r0 = pg_exec($c0, $q0);

 for( $i=0; $row = @pg_fetch_array($r0,$i); $i++){
   echo "<tr>
    <td>". $row['station'] ."</td>
    <td>". $row['valid'] ."</td>
    <td>". $row['high'] ."</td>
    <td>". $row['low'] ."</td>
    <td>". $row['precip'] ."</td>
    <td>". $row['reports'] ."</td>
     </tr>\n";
 } // End of for loop
?>

</table>

<?php include("../../include/footer2.php"); ?>
