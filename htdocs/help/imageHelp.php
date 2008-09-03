<?php 
 include("../../config/settings.inc.php");
	$title = "IEM | Image Help";
	include("$rootpath/include/header.php"); 
	include("$rootpath/include/database.inc.php"); 
 $iod = isset($_GET['iod']) ? intval($_GET['iod']) : 1;
?>

<TR>

<TD valign="top" colspan="5">

<?php
  $connection = iemdb("mesosite");
  $result = pg_prepare($connection, "query", "SELECT * from image_help WHERE iod = $1");
  $result = pg_execute($connection, "query", array($iod) );

          $row = @pg_fetch_array($result, 0);
          $body = $row["body"];
          $title = $row["title"];
          $ahref = $row["ahref"];

	  $fileL = $rootpath ."htdocs/". $ahref ;

	  $fileInfo = stat( $fileL );
	  $suffix = substr( $fileL, -3 );


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
