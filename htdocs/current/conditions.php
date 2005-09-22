<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
        <TITLE>IEM | Current Conditions</TITLE>
        <META NAME="AUTHOR" CONTENT="Daryl Herzmann">
        <link rel="stylesheet" type="text/css" href="/css/mesonet.css">
</HEAD>

<body>

<?php 
        include("../include/header2.php"); 
?>

<?php include("../include/imagemaps.php"); ?>


<?php
	include("../include/asosLoc.php");
	include("../include/awosLoc.php");
	include("../include/rwisLoc.php");

	print "<BR><BR>";

	if ( strlen( $rwis ) > 0 ) {
		print "<P>Please select a RWIS station";
		print "<BR> or switch to <a href=\"conditions.php\">ASOS / AWOS </a> stations."; 
		echo print_rwis("conditions.php?rwisStation=yes&station");

	} elseif ( $station == "") {
		print "<P>Please select an ASOS/AWOS station";
		print "<BR>or switch to <a href=\"conditions.php?rwis=yes\">RWIS</a> stations.";
		echo print_asos("conditions.php?station");

	} else {
		if ( strlen($rwisStation) > 0 ) {
			$stationTable = "rtransfer";
			print "<P><a href='conditions.php?rwis=yes'>Different Location</A><BR>";
		} else {
			$stationTable = "transfer";
			print "<P><a href='conditions.php'>Different Location</A><BR>";
		}

		$connection = pg_connect("localhost", "5432", "compare");

		$query = "SELECT to_char(valid, 'MM/DD/YY HH:MI PM') , tmpf::int, dwpf::int, sknt, drct from ". $stationTable ." WHERE station = '" . $station . "' ORDER by valid DESC LIMIT 1 ";
		
		$query2 = "SELECT to_char(valid, 'MM/DD/YY HH:MI PM'), tmpf from ". $stationTable ." WHERE tmpf = (SELECT max(tmpf) as max_tmpf from ". $stationTable ." WHERE station = '" . $station . "' and (valid + '24 hours'::interval ) > CURRENT_TIMESTAMP ) and station = '" . $station . "' and (valid + '24 hours'::interval ) > CURRENT_TIMESTAMP ";
                 
                $query2_5 = "SELECT to_char(valid, 'MM/DD/YY HH:MI PM'), tmpf from ". $stationTable ." WHERE tmpf = (SELECT min(tmpf) as max_tmpf from ". $stationTable ." WHERE station = '" . $station . "' and (valid + '24 hours'::interval ) > CURRENT_TIMESTAMP ) and station = '" . $station . "' and (valid + '24 hours'::interval ) > CURRENT_TIMESTAMP ";


		$query3 = "SELECT to_char(valid, 'MM/DD/YY HH:MI PM'), tmpf from ". $stationTable ." WHERE tmpf = (SELECT max(tmpf) as max_tmpf from ". $stationTable ." WHERE station = '" . $station . "' and date( valid ) = 'TODAY' ) and station = '" . $station . "' and date( valid ) = 'TODAY'";
		
		$query3_5 = "SELECT to_char(valid, 'MM/DD/YY HH:MI PM'), tmpf from ". $stationTable ." WHERE tmpf = (SELECT min(tmpf) as max_tmpf from ". $stationTable ." WHERE station = '" . $station . "' and date( valid ) = 'TODAY' ) and station = '" . $station . "' and date( valid ) = 'TODAY'";
		$result = pg_exec($connection, $query );
		$result2 = pg_exec($connection, $query2 );
		$result2_5 = pg_exec($connection, $query2_5 );
		$result3 = pg_exec($connection, $query3 );
		$result3_5 = pg_exec($connection, $query3_5 );

		if (pg_numrows( $result ) > 0) {
			$row = pg_fetch_row($result, 0);
			$row2 = pg_fetch_row($result2, 0);
			$row2_5 = pg_fetch_row($result2_5, 0);
			$row3 = pg_fetch_row($result3, 0);
			$row3_5 = pg_fetch_row($result3_5, 0);

			$tester = $Acities[$station]["city"];
			if ( strlen($tester) == 0 ) {
				$tester = $Wcities[$station]["city"];
				if ( strlen($tester) == 0 ) {
					$tester = $Rcities[$station]["city"];
				}
			}


			print "<BR><BR><TABLE>\n";
			print "<TR><TH>Location </TH><TD>" . $tester . " ( ". $station ." )</TD></TR>\n";
			print "<TR bgcolor=\"#EEEEEE\"><TH>Last Observation </TH><TD>" . $row[0] . " (Local Time)</TD></TR>\n";
        		print "<TR><TH>Current Temperature </TH><TD>" . $row[1] . "</TD></TR>\n";
        		print "<TR bgcolor=\"#EEEEEE\"><TH>Current Dew Point </TH><TD>" . $row[2] . "</TD></TR>\n";
			print "<TR><TH>Wind Speed (knots) </TH><TD>" . $row[3] . "</TD></TR>\n";
			print "<TR bgcolor=\"#EEEEEE\"><TH>Wind Direction  </TH><TD>" . $row[4] . "</TD></TR>\n";
			print "</TABLE>\n";

			print "<BR>\n";


			print "<TABLE cellpadding=3 width=100%>\n";
			print "<TR><TD></TD><TH>Last 24 Hours:</TH><TH>Today:</TH></TR>\n";
			print "<TR><TH>Max Temp</TH><TD><font color=\"red\">" . $row2[1] ."</font> (<i>" . $row2[0] ."</i>)</TD>";
			print "<TD><font color=\"red\">" . $row3[1] ."</font> (<i>" . $row3[0] ."</i>)</TD></TR>\n";
			print "<TR><TH>Min Temp</TH><TD><font color=\"blue\">" . $row2_5[1] ."</font> (<i>" . $row2_5[0] ."</i>)</TD>";
			print "<TD><font color=\"blue\">" . $row3_5[1] ."</font> (<i>" . $row3_5[0] ."</i>)</TD></TR>\n";
			print "</TABLE>\n";

			print "<BR><BR>\n";
	                print "<img src=\"/plotting/24h/1temps.php?station=". $station ."\" ALT=\"Time Series\"><BR>\n";
                        print "<img src=\"/plotting/24h/winds.php?station=". $station ."\" ALT=\"Time Series\">\n";


		} else {
			echo "No Obs found for this station: $station ";
		}
		pg_close($connection);

	}
?>
<?php
	include("../include/footer2.php");

?>
