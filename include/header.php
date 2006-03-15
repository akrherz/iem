<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<title><?php echo isset($TITLE) ? $TITLE: "Iowa Environmental Mesonet"; ?></title>
 <link rel="stylesheet" type="text/css" href="<?php echo $rooturl; ?>/css/main.css" />
 <link rel="stylesheet" type="text/css" href="<?php echo $rooturl; ?>/css/main-theme.css" />
 <link rel="alternate stylesheet" type="text/css" media="screen" href="<?php echo $rooturl; ?>/css/red.css"
title="red" />
 <link rel="alternate stylesheet" type="text/css" media="screen" href="<?php echo $rooturl; ?>/css/slashdot.css" title="slashdot" />
 <script type="text/javascript" src="<?php echo $rooturl; ?>/js/styleswitcher.js"></script>
 <?php if (isset($REFRESH)){ echo $REFRESH; } ?>
 <?php if (isset($HEADEXTRA)){ echo $HEADEXTRA;} ?>
</head>
<body <?php if (isset($BODYEXTRA)){ echo $BODYEXTRA;} ?>>
<?php include("$rootpath/include/webring.html"); ?>
<div id="iem-main">
 
<div id="iem-header">
 
<div id="iem-header-logo">
<a href="<?php echo $rooturl; ?>/"><img src="<?php echo $rooturl; ?>/images/logo_small.gif" alt="IEM" /></a>
</div>
                                                                                
<div id="iem-header-title">
<h3>Iowa Environmental Mesonet</h3>
<h4>Iowa State University Department of Agronomy</h4>
</div>
                                                                                
<div id="iem-header-items">
<b>Select Theme:</b>
<br /><a title="Small Text Size" class="navSmallText" href="#" onclick="setActiveStyleSheet('default'); return false">Default</a>
| <a title="Small Text Size" class="navSmallText" href="#" onclick="setActiveStyleSheet('red'); return false">Red</a>
| <a title="Small Text Size" class="navSmallText" href="#" onclick="setActiveStyleSheet('slashdot'); return false">Slashdot</a>
</div>
                                                                                
<div class="iem-menu">
 <a href="<?php echo $rooturl; ?>/archive/">Archive</a>
 &middot; <a href="<?php echo $rooturl; ?>/current/">Current</a>
 &middot; <a href="<?php echo $rooturl; ?>/climate/">Climatology</a>
 &middot; <a href="<?php echo $rooturl; ?>/climodat/">Climodat</a>
 &middot; <a href="<?php echo $rooturl; ?>/cool/">Cool Stuff</a>
 &middot; <a href="<?php echo $rooturl; ?>/sites/locate.php">IEM Sites</a>
 &middot; <a href="<?php echo $rooturl; ?>/GIS/">GIS</a>
 &middot; <a href="<?php echo $rooturl; ?>/info.php">Info</a>
 &middot; <a href="<?php echo $rooturl; ?>/QC/">Quality Control</a>
</div>
</div><!-- End of iem-header -->
<?php 
include("$rootpath/include/warnings/inc.phtml"); ?>
<div id="iem-content">
