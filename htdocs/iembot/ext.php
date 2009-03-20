<?php
include("../../config/settings.inc.php");

$HEADEXTRA = '<link rel="stylesheet" type="text/css" href="../ext/resources/css/ext-all.css"/>
<script type="text/javascript" src="../ext/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="../ext/ext-all.js"></script>
<script type="text/javascript" src="wfos.js"></script>
<script type="text/javascript" src="static.js?v=1.0.1"></script>';
$TITLE = "iembot web based monitor";
$NOCONTENT = 1;
$THISPAGE ="severe-iembot";
include("$rootpath/include/header.php");
?>
<style>
<style type="text/css">
.message {
  white-space: normal;
  padding-left: 15px;
}
td.x-grid3-td-message {
    overflow: hidden;
}
td.x-grid3-td-message div.x-grid3-cell-inner {
    white-space: normal;
}
</style>
</style>
<div id="help">
boom
</div>
<script>
Ext.onReady(function(){

});
</script>
<?php include("$rootpath/include/footer.php"); ?>
