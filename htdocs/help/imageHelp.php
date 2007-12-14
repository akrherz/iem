<?php 
 include("../../config/settings.inc.php");
	$title = "IEM | Image Help";
	include("$rootpath/include/header.php"); 
	include("$rootpath/include/database.inc.php"); 
 $iod = isset($_GET['iod']) ? $_GET['iod'] : 1;
?>

<TR>

<TD valign="top" colspan="5">

<?php
	$connection = iemdb("mesosite");

	echo " &nbsp; <b>|</b> &nbsp; <a href=\"http://mesonet.agron.iastate.edu\">Mesonet Homepage</a>\n";
	echo " &nbsp; <b>|</b> &nbsp; \n";

	  $query = "SELECT * from image_help WHERE iod = ". $iod ." ";
	  $result = pg_exec($connection, $query);
          $row = @pg_fetch_array($result, 0);
          $body = $row["body"];
          $title = $row["title"];
          $ahref = $row["ahref"];

	  $fileL = "/home/httpd/html/". $ahref ;

	  $fileInfo = stat( $fileL );
	  $suffix = substr( $fileL, -3 );

	  echo " <a href=\"imageHelp.php\">List All Images</a> &nbsp; <b>|</b> &nbsp; \n";

	  echo "<P><B>". $title ."</B>\n";
	  echo "<P><font class=\"info\">". $body ."</font>\n";
	  if ( $suffix != "txt" ){
	    echo "<h3>Current Image:</h3><BR>\n<img src=\"". $ahref ."\">";
	  } else {
	    echo "<h3>File Contents:</h3><BR>";
	    echo "<PRE>\n";
	    include( $fileL );
	    echo "</PRE>\n";
          }
	  echo "<h3>File Information:</h3>\n";
	  if ( is_file( $fileL ) ){
	    echo "<TABLE>\n";
	    echo "<TR><TH>Creation Date:</TH><TD> ". gmdate("M dS H:i T" ,$fileInfo[9]) ."</TD></TR>\n";
	    echo "<TR><TH>File Size:</TH><TD> ". $fileInfo[7] ." Bytes</TD></TR>\n";
	    echo "</TABLE>\n";
	  } else {
	    echo "This image was dynamically generated.";
	  }


	pg_close($connection);

?>





</TD></TR>

<?php include("$rootpath/include/footer.php"); ?>
