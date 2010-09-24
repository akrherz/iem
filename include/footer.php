<?php if (! isset($NOCONTENT)) echo "</div><!-- End #iem-content -->"; ?>
<div id="iem-footer">

<div style="float: right;">
 <form method="get" action="http://www.google.com/search" name="search">
 <b>Search Site with Google:</b><br />
 <input value="mesonet.agron.iastate.edu" name="sitesearch" type="hidden" />
<input type="text" size="15" name="q" /><input type="submit" value="Search" /></form>
</div>

Copyright &copy; 2001-<?php echo date("Y"); ?>, Iowa State University of Science and Technology.
<br />All rights reserved.
 <a href="<?php echo $rooturl; ?>/help/abbreviations.php">abbreviations</a>
 &middot; <a href="<?php echo $rooturl; ?>/info/contacts.php">contact us</a>
 &middot; <a href="https://trac.agron.iastate.edu/trac/IEM">development</a>
 &middot; <a href="<?php echo $rooturl; ?>/disclaimer.php">disclaimer</a>
</div>
<?php if (! isset($NOCONTENT)) echo "</div> <!-- End of iem-main -->"; ?>
</body>
</html>
