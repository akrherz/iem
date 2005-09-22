<?php 
 include("../../config/settings.inc.php");
        $TITLE = "ISU Ag Climate";
        include("$rootpath/include/header.php"); 

 $src = $_GET["src"];
?>
<div class="text">
<a href="<?php echo $rooturl; ?>/agclimate/">ISU AgClimate</a>

<table style="float: left;" width="100%">
<TR>
<TD valign="top">

<img src="<?php echo $rooturl . $src; ?>" ALT="ISU Ag Climate">

<p><font class="bluet">QC Flags</font>
<table>
<tr>
  <th>M</th>
  <td>the data is missing</td></tr>

<tr>
  <th>E</th>
  <td>An instrument may be flagged until repaired</td></tr>

<tr>
  <th>R</th>
  <td>Estimate based on weighted linear regression from surrounding stations</td></tr>

<tr>
  <th>e</th>
  <td>We are not confident of the estimate</td></tr>

</table>


</TD>
<TD valign="TOP" width="250">

	<?php include("include/dataLinks.php"); ?>

</TD></TR>
</table>

<br clear="all" /><p>&nbsp;</p>
</div>

<?php include("$rootpath/include/footer.php"); ?>
