<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"></meta>
<link rel="stylesheet" href="layersmenu-demo.css" type="text/css"></link>
<link rel="stylesheet" href="layersmenu-old.css" type="text/css"></link>
<link rel="stylesheet" href="layersmenu-gtk2.css" type="text/css"></link>
<link rel="stylesheet" href="layersmenu-keramik.css" type="text/css"></link>
<link rel="stylesheet" href="layersmenu-galaxy.css" type="text/css"></link>
<link rel="stylesheet" href="layerstreemenu.css" type="text/css"></link>
<style type="text/css">
<!--
@import url("layerstreemenu-hidden.css");
//-->
</style>
<link rel="shortcut icon" href="LOGOS/shortcut_icon_phplm.png"></link>
<title>The PHP Layers Menu System</title>
<?php include ("libjs/layersmenu-browser_detection.js"); ?>
<script language="JavaScript" type="text/javascript" src="libjs/layersmenu-library.js"></script>
<script language="JavaScript" type="text/javascript" src="libjs/layersmenu.js"></script>
<script language="JavaScript" type="text/javascript" src="libjs/layerstreemenu-cookies.js"></script>

<?php
include ("lib/PHPLIB.php");
include ("lib/layersmenu-common.inc.php");
include ("lib/layersmenu.inc.php");

$mid = new LayersMenu();

$mid->setMenuStructureFile("layersmenu-horizontal-1.txt");
$mid->parseStructureForMenu("hormenu1");
$mid->setHorizontalMenuTpl("layersmenu-horizontal_menu-full.ihtml");
$mid->newHorizontalMenu("hormenu1");

$menustring =
".|Linus B. Torvalds|http://www.cs.Helsinki.FI/u/torvalds/|The father of Linux||Linus\n" .
".|Linux Kernel Archives|http://www.kernel.org/|Here you can download the Linux kernel sources|www.kernel.org_images_tux16-16.png|kernelorg\n" .
".|Linux Distributions|http://flashnet.linux.tucows.com/distribution.html|Here you can find a list of the major Linux distributions||Linux|1\n" .
"..|Debian GNU/Linux|http://www.debian.org/|Enjoy the exciting world of Debian GNU/Linux!|debian-icon-mini.png|Linux|1\n" .
"...|About|http://www.debian.org/intro/about|||Linux\n" .
"...|News|http://www.debian.org/News/|||Linux\n" .
"...|Distribution|http://www.debian.org/distrib/|||Linux\n" .
"...|Support|http://www.debian.org/support|||Linux\n" .
"...|Development|http://www.debian.org/devel/|||Linux\n" .
"...|Search|http://search.debian.org/|||Linux\n" .
"...|A Debian Mirror|http://ftp.mirror.ac.uk/sites/ftp.debian.org/|||Linux\n" .
"..|Mandrake|http://www.mandrakelinux.com/|Mandrake Linux||Linux\n" .
"...|Errata|http://www.mandrakelinux.com/en/errata.php3|||Linux\n" .
"...|Download|http://www.mandrakelinux.com/en/ftp.php3|||Linux\n" .
"...|Mandrake Expert|http://www.mandrakeexpert.com/index1.php|||Linux\n" .
"...|Bugzilla|http://qa.mandrakesoft.com/|||Linux\n" .
"..|Slackware|http://www.freesoftware.org/|Slackware Linux||Linux\n";
$mid->setMenuStructureString($menustring);
$mid->parseStructureForMenu("vermenu1");
$mid->setDownArrowImg("down-galaxy.png");
$mid->setForwardArrowImg("forward-galaxy.png");
$mid->setVerticalMenuTpl("layersmenu-vertical_menu-galaxy.ihtml");
$mid->setSubMenuTpl("layersmenu-sub_menu-galaxy.ihtml");
$mid->newVerticalMenu("vermenu1");

$mid->setMenuStructureFile("layersmenu-vertical-2.txt");
$mid->parseStructureForMenu("vermenu2");
$mid->setDownArrowImg("down-gtk2.png");
$mid->setForwardArrowImg("forward-gtk2.png");
$mid->setVerticalMenuTpl("layersmenu-vertical_menu.ihtml");
$mid->setSubMenuTpl("layersmenu-sub_menu.ihtml");
$mid->newVerticalMenu("vermenu2");

$mid->setMenuStructureFile("layersmenu-horizontal-2.txt");
$mid->parseStructureForMenu("hormenu2");
$mid->setDownArrowImg("down-keramik.png");
$mid->setForwardArrowImg("forward-keramik.png");
$mid->setHorizontalMenuTpl("layersmenu-horizontal_menu-keramik.ihtml");
$mid->setSubMenuTpl("layersmenu-sub_menu-keramik.ihtml");
$mid->newHorizontalMenu("hormenu2");


$mid->printHeader();
?>

</head>
<body>

<?php $mid->printMenu("hormenu1"); ?>

<div class="normalbox">
<div class="h1">The PHP Layers Menu System</div>
</div>

<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tr>
<td width="20%" valign="top">

<div class="normalbox">
<div class="normal">
A vertical menu...
</div>
</div>
<center>
<?php $mid->printMenu("vermenu1"); ?>
</center>

<div class="normalbox">
<div class="normal">
Tree Menu version
</div>
<?php
include ("lib/treemenu.inc.php");
$treemid = new TreeMenu();
$treemid->setMenuStructureFile("layersmenu-vertical-1.txt");
$treemid->parseStructureForMenu("treemenu1");
print $treemid->newTreeMenu("treemenu1");
?>
</div>

<div class="normalbox">
<div class="normal">
PHP Tree - No JavaScript
</div>
<?php
include ("lib/phptreemenu.inc.php");
$phptreemid = new PHPTreeMenu();
$phptreemid->setPHPTreeMenuDefaultExpansion("3|4|18");
$phptreemid->setMenuStructureFile("layersmenu-vertical-1.txt");
$phptreemid->parseStructureForMenu("treemenu1");
print $phptreemid->newPHPTreeMenu("treemenu1");
?>
</div>

<div class="normalbox">
<div class="normal">
Plain - No JavaScript
</div>
</div>
<center>
<?php
include ("lib/plainmenu.inc.php");
$plainmid = new PlainMenu();
$plainmid->setMenuStructureFile("layersmenu-vertical-1.txt");
$plainmid->parseStructureForMenu("treemenu1");
print $plainmid->newPlainMenu("treemenu1");
?>
</center>

<br />

<div class="normalbox">
<div class="normal">
Another vertical menu...
</div>
</div>
<center>
<?php $mid->printMenu("vermenu2"); ?>
</center>

<div class="normalbox">
<div class="normal">
PHP Tree - No JavaScript
</div>
<?php
$phptreemid->setMenuStructureFile("layersmenu-vertical-2.txt");
$phptreemid->parseStructureForMenu("treemenu2");
print $phptreemid->newPHPTreeMenu("treemenu2");
?>
</div>

<br />
<center>
<a href="http://phplayersmenu.sourceforge.net/"><img border="0"
src="LOGOS/powered_by_phplm.png" alt="Powered by PHP Layers Menu" height="31" width="88" /></a>
</center>
<br />
<center>
<a href="http://validator.w3.org/check/referer"><img border="0"
src="images/valid-xhtml10.png" alt="Valid XHTML 1.0!" height="31" width="88" /></a>
</center>
<br />
<center>
<a href="http://jigsaw.w3.org/css-validator/"><img border="0"
src="images/vcss.png" alt="Valid CSS!" height="31" width="88" /></a>
</center>

</td>
<td valign="top">

<div class="normalbox">

<div class="normal" align="center">
Another horizontal menu... and its <a href="layersmenu-horizontal-2.txt" target="TheMenuStructureFile">Menu Structure File</a>
<div style="height: 2px"></div>
<?php $mid->printMenu("hormenu2"); ?>
</div>

<table cellspacing="0" cellpadding="5" border="0">
<tr>
<td class="normal" valign="top">

Tree Menu version
<?php
$treemid->setMenuStructureFile("layersmenu-horizontal-2.txt");
$treemid->parseStructureForMenu("treemenu3");
print $treemid->newTreeMenu("treemenu3");
?>

</td>
<td class="normal" valign="top">

Horizontal Plain version - No JavaScript
<?php
$pmid = new PlainMenu();
$pmid->setMenuStructureFile("layersmenu-horizontal-2.txt");
$pmid->parseStructureForMenu("phormenu");
print $pmid->newHorizontalPlainMenu("phormenu");
?>

</td>
</tr>
</table>

</div>

<div class="normalbox">
<div class="normal">
<?php include ("README.ihtml"); ?>
</div>
</div>

</td>
</tr>
</table>

<?php
$mid->printFooter();
?>

</body>
</html>
