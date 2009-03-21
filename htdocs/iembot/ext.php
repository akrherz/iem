<?php
include("../../config/settings.inc.php");

$HEADEXTRA = '<link rel="stylesheet" type="text/css" href="../ext/resources/css/ext-all.css"/>
<script type="text/javascript" src="../ext/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="../ext/ext-all-debug.js"></script>
<script type="text/javascript" src="channels.js"></script>
<script type="text/javascript" src="static.js?v=1.0.1"></script>';
$TITLE = "iembot web based monitor";
$NOCONTENT = 1;
$THISPAGE ="severe-iembot";
include("$rootpath/include/header.php");
?>
<style type="text/css">
.new-tab{
  background-image:url(new_tab.gif) !important;
}
td.x-grid3-td-message {
    overflow: hidden;
}
td.x-grid3-td-message div.x-grid3-cell-inner {
    white-space: normal;
}
</style>
<div id="help">
boom
</div>
<script>
Ext.onReady(function(){

});
</script>
<?php include("$rootpath/include/footer.php"); ?>
