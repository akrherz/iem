<?php 
include("../../config/settings.inc.php");
$sortcol = isset($_GET["sortcol"]) ? $_GET["sortcol"] : "sid";
function aSortBySecondIndex($multiArray, $secondIndex) {
        while (list($firstIndex, ) = each($multiArray))
                $indexMap[$firstIndex] = $multiArray[$firstIndex][$secondIndex];
        asort($indexMap);
        while (list($firstIndex, ) = each($indexMap))
                if (is_numeric($firstIndex))
                        $sortedArray[] = $multiArray[$firstIndex];
                else $sortedArray[$firstIndex] = $multiArray[$firstIndex];
        return $sortedArray;
}

$TITLE = "IEM | School Network | History";
$THISPAGE="networks-schoolnet";
include("$rootpath/include/header.php"); 
?>


<?php
 $data = Array();
 $fc = file('history.dat');
 while (list ($line_num, $line) = each ($fc)) {
   $tokens = split ("\|", $line);
   $data[ $tokens[0] ] = Array( "sid" => $tokens[0], "sname" => $tokens[1], "sts" => $tokens[2] );
 } // End of while

 $data = aSortBySecondIndex($data, $sortcol);
?>
<h3 class="heading">SchoolNet Archive Listing</h3>
<div class="text">
<p>The IEM began archiving schoolnet data on the 12th of Feb, 2002.  Since
that time, some stations have been added to the network.  Here is a listing of sites and 
the first observation recorded in the archive.</p>

  <table>
  <tr>
    <th><a href='history.php?sortcol=sid'>Site ID:</a></th>
    <th><a href='history.php?sortcol=sname'>Site Name:</a></th>
    <th><a href='history.php?sortcol=sts'>Archive Begins:</a></th>
  </tr>

<?php
 while (list ($key, $val) = each ($data))  { 
   echo "<tr><td>".$key."</td><td>". $data[$key]["sname"]."</td><td>". $data[$key]["sts"] ."</td></tr>\n";
 }
 echo "</table>";
?>

</div>

 
<?php include("$rootpath/include/footer.php"); ?>
