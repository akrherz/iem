<?php 

$station1 = strtoupper($station1);
$station2 = strtoupper($station2);

	$TITLE = "IEM | 24 Hour Comparison";
include("/mesonet/php/include/header.php"); 
	include("../../include/imagemaps.php");
?>
<div class="text">
<b>Nav:</b> <a href="/schoolnet/">School Net</a> <b> > </b>
  <a href="/plotting/snet">Plotting</a> <b> > </b>
  <b>Comparisons</b>

<p> This program will create a side-by-side plot of an atmospheric variable for
two stations.  Please make the necessary selections in order for the plot to work.  If you 
receive a broken image symbol, data is missing for your station locations.</p>

<CENTER>
<TABLE border="0">
<TR>
	<TH bgcolor="#EEEEEE">Select Locations Either:</TH>
	<TD><a href="2compare.php">Graphically</a></TD>
	<TD> or <a href="2compare.php?graph=text">Textual</a></TD>
</TR></TABLE>
</CENTER>


<?php
if ( strlen($graph) > 0 ) { ?>

<H3 class="subtitle">Textual Selection:</H3>

<FORM METHOD="GET" action="2compare.php">
<p class="story"><b>Hint.</b>  ASOS/AWOS stations have 3 character IDs, the 
RWIS have 4 and start with R, the School Net stations have 4 and start with
S.</p>
<P>Enter station 1: <INPUT TYPE="TEXT" NAME="station1" value="<?= $station1 ?>">
<P>Enter station 2: <INPUT TYPE="TEXT" NAME="station2" value="<?= $station2 ?>">

<P>Data Plotted: <SELECT name="data">
<option value="tmpf">Temperature
<option value="dwpf">Dewpoint
<option value="sknt">Wind Speed (knots)
</SELECT>

<P><INPUT TYPE="SUBMIT" VALUE="Make Map">

</FORM>

<?php
// We have a good Request
} elseif (strlen($station1) > 0 && strlen($station2) > 0 && strlen($data) > 0) {
?>

<ul>
        <li>First Station: <?= $station1 ?> &nbsp; <a href="2compare.php?station1=<?= $station2 ?>">Change</a></li>
        <li>Second Station: <?= $station2 ?> &nbsp; <a href="2compare.php?station1=<?= $station1 ?>">Change</a></li>
</ul>

<P><a href="2compare.php">Start Over</a>
<P>
<BR><BR>

<img src="2temps.php?station1=<?= $station1 ?>&station2=<?= $station2 ?>&data=<?= $data ?>" ALT="Time Series">
</CENTER>

<BR>
 
<P>Data only valid within the past 24 hours is displayed on this chart.
 
<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has
missing data. 
 
<BR><BR> 


<?php
} elseif (strlen($station1) > 0 && strlen($station2) > 0 && strlen($data) == 0) {

?>
<p><font class="bluet">Finalize Plot Generation:</font><p>
<p class="story">Please select which variable you would like compared.</p>

<FORM METHOD="GET" action="2compare.php">
<P>Enter station 1: <INPUT TYPE="TEXT" NAME="station1" value="<?= $station1 ?>">
<P>Enter station 2: <INPUT TYPE="TEXT" NAME="station2" value="<?= $station2 ?>">

<P>Data Plotted: <SELECT name="data">
<option value="tmpf">Temperature
<option value="dwpf">Dewpoint
<option value="sknt">Wind Speed (knots)
</SELECT>

<P><INPUT TYPE="SUBMIT" VALUE="Make Map">



<?php
} elseif ( strlen($station1) > 0 && strlen($station2) == 0 ) {
?>
<ul>
	<li>First Station: <?= $station1 ?> &nbsp; <a href="2compare.php">Change</a></li>
</ul>

<p><h3 class="subtitle">Graphic Selection:</h3><p>
<p class="story">Please select a second station from below, or switch to a different network for the 
second station.</p>

	<?php  if ($network == "rwis") { ?> 
		<table><tr>
		 <th>Networks:</th>
		 <td><a href="2compare.php?network=asos&station1=<?= $station1 ?>">ASOS</a></td>
		 <td><b>RWIS</b></td>
		 <td><a href="2compare.php?network=school&station1=<?= $station1 ?>">School Net</a></td>
		</tr></table><p>
		<?php
		echo print_rwis("2compare.php?station1=". $station1 ."&station2");

	} else if ($network == "school"){ ?> 
		<table><tr>
		 <th>Networks:</th>
		 <td><a href="2compare.php?network=asos&station1=<?= $station1 ?>">ASOS</a></td>
		 <td><a href="2compare.php?network=rwis&station1=<?= $station1 ?>">RWIS</a></td>
		 <td><b>School Net</b></td>
		</tr></table><p>
		
		<?php
		echo print_snet("2compare.php?station1=". $station1 ."&station2"
);
	} else { ?> 
		<table><tr>
		 <th>Networks:</th>
		 <td><b>ASOS</b></td>
		 <td><a href="2compare.php?network=rwis&station1=<?= $station1 ?>">RWIS</a></td>
		 <td><a href="2compare.php?network=school&station1=<?= $station1 ?>">School Net</a></b></td>
		</tr></table><p>
		<?php
		echo print_asos("2compare.php?station1=". $station1 ."&station2");
	}

} else {
?>
 <p><h3 class="subtitle">Graphic Selection:</h3><p>
 <p class="story">Please select from one of the stations below, or swich to 
 a different network.</p>
 <?php  if ($network == "rwis") { ?> 
 		<table><tr>
		 <th>Networks:</th>
		 <td><a href="2compare.php?network=asos">ASOS</a></td>
		 <td><b>RWIS</b></td>
		 <td><a href="2compare.php?network=school">School Net</a></td>
		</tr></table><p>
		<?php
                echo print_rwis("2compare.php?station1");
 
        } else if ($network == "school"){ ?> 
		<table><tr>
		 <th>Networks:</th>
		 <td><a href="2compare.php?network=asos">ASOS</a></td>
		 <td><a href="2compare.php?network=rwis">RWIS</a></td>
		 <td><b>School Net</b></td>
		</tr></table><p>
		<?php
                echo print_snet("2compare.php?station1");

	} else { ?> 
		<table><tr>
		 <th>Networks:</th>
		 <td><b>ASOS</b></td>
		 <td><a href="2compare.php?network=rwis">RWIS</a></td>
		 <td><a href="2compare.php?network=school">School Net</a></b></td>
		</tr></table><p>
		<?php
                echo print_asos("2compare.php?station1");
        }
}
?>
</div>


<?php include("/mesonet/php/include/footer.php"); ?>
