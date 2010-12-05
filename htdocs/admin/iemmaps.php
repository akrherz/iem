<?php
include("../../config/settings.inc.php");
/*
 * Allow me to create entries in the database
 * 
 */
include("$rootpath/include/header.php");
include("$rootpath/include/database.inc.php");
$mesosite = iemdb('mesosite');
$rs = pg_prepare($mesosite, "INSERT", "INSERT into iemmaps" .
		"(title, description, keywords, ref, category)" .
		"VALUES ($1, $2, $3, $4, $5)");
if (isset($_REQUEST["title"])){
	pg_execute($mesosite, "INSERT", Array(
		$_REQUEST["title"], $_REQUEST["description"],
		$_REQUEST["keywords"], $_REQUEST["ref"],
		$_REQUEST["category"]
	));
	echo "Insert Complete!";
}

?>

<form method="POST" name="myform">

<p><b>Title:</b> <input type="text" name="title" />

<p><b>Keywords:</b> <input type="text" name="keywords" />

<p><b>Image Reference:</b> <input type="text" name="ref" />

<p><b>Category:</b> <input type="text" name="category" />

<p><b>Description:</b><br />
<textarea NAME='description' wrap="hard" ROWS="20" COLS="70"></textarea></p>

<p><input type="submit" />
</form>

<?php include("$rootpath/include/footer.php"); ?>