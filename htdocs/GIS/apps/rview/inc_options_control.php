<p><strong>Map Extent:</strong>
<br />View Scale: <select name="zoom">
 <option value="25" <?php if ($zoom == 25) echo "SELECTED"; ?>>25km
 <option value="50" <?php if ($zoom == 50) echo "SELECTED"; ?>>50km
 <option value="100" <?php if ($zoom == 100) echo "SELECTED"; ?>>100km
 <option value="250" <?php if ($zoom == 250) echo "SELECTED"; ?>>250km
 <option value="500" <?php if ($zoom == 500) echo "SELECTED"; ?>>500km
 <option value="1000" <?php if ($zoom == 1000) echo "SELECTED"; ?>>1000km
 <option value="3000" <?php if ($zoom == 3000) echo "SELECTED"; ?>>3000km
</select>

<br />Image Size:
<select name="imgsize">
 <option value="640x480" <?php if ($imgsize == "640x480") echo "SELECTED"; ?>>640x480
 <option value="800x600" <?php if ($imgsize == "800x600") echo "SELECTED"; ?>>800x600
 <option value="1024x768" <?php if ($imgsize == "1024x768") echo "SELECTED"; ?>>1024x768
 <option value="1280x1024" <?php if ($imgsize == "1280x1024") echo "SELECTED"; ?>>1280x1024
</select>

<p><strong>Loop Options</strong>
<br /><select name="loop">
  <option value="0" <?php if ($loop == 0) echo "SELECTED"; ?>>1 image only
  <option value="1" <?php if ($loop == 1) echo "SELECTED"; ?>>Java Script Loop
  <option value="2" <?php if ($loop == 2) echo "SELECTED"; ?>>Java Applet Loop
</select>
<br />Loop Frames: 
<input type="text" value="<?php echo $frames; ?>" name="frames" size="3">
<br />Loop Frame Interval: 
<select name="interval">
  <option value="5" <?php if ($interval == 5) echo "SELECTED"; ?>>5 minutes
  <option value="10" <?php if ($interval == 10) echo "SELECTED"; ?>>10 minutes
  <option value="15" <?php if ($interval == 15) echo "SELECTED"; ?>>15 minutes
  <option value="30" <?php if ($interval == 30) echo "SELECTED"; ?>>30 minutes
  <option value="60" <?php if ($interval == 60) echo "SELECTED"; ?>>1 hour
  <option value="120" <?php if ($interval == 120) echo "SELECTED"; ?>>2 hours
  <option value="1440" <?php if ($interval == 1440) echo "SELECTED"; ?>>1 day
</select>

<p><strong>Text Warning Listing</strong>
<br />Filter by WFO:<select name="filter">
  <option value="0" <?php if ($filter == 0) echo "SELECTED"; ?>>No
  <option value="1" <?php if ($filter == 1) echo "SELECTED"; ?>>Yes
</select>

<br />Product Filter: 
<br /><input type="radio" value="0" name="cu" <?php if ($cu == 0) { echo "checked"; } ?>>Show All
<br /><input type="radio" value="1" name="cu" <?php if ($cu == 1) { echo "checked"; } ?>>Convective Only

<br />Sort Column:
<select name="sortcol">
  <option value="fcster" <?php if ($sortcol == "fcster") echo "SELECTED"; ?>>Product Author
  <option value="phenomea" <?php if ($sortcol == "phenomena") echo "SELECTED"; ?>>Product Type
  <option value="expire" <?php if ($sortcol == "expire") echo "SELECTED"; ?>>Product Expiration
  <option value="issue" <?php if ($sortcol == "issue") echo "SELECTED"; ?>>Product Issued
  <option value="sname" <?php if ($sortcol == "sname") echo "SELECTED"; ?>>State Name
  <option value="updated" <?php if ($sortcol == "updated") echo "SELECTED"; ?>>Product Updated
  <option value="wfo" <?php if ($sortcol == "wfo") echo "SELECTED"; ?>>Weather Office
  <option value="eventid" <?php if ($sortcol == "eventid") echo "SELECTED"; ?>>VTEC Event ID
  <option value="status" <?php if ($sortcol == "status") echo "SELECTED"; ?>>VTEC Status
</select>

<br />Sort Direction:<select name="sortdir">
  <option value="0" <?php if ($sortdir == 0) echo "SELECTED"; ?>>DESC
  <option value="1" <?php if ($sortdir == 1) echo "SELECTED"; ?>>ASC
</select>

<p><strong>Local Storm Reports</strong>
<br />Direction in time:<select name="lsrlook">
 <option value="+" <?php if ($lsrlook == "+") echo "SELECTED" ?>>+
 <option value="-" <?php if ($lsrlook == "-") echo "SELECTED" ?>>-
 <option value="+/-" <?php if ($lsrlook == "+/-") echo "SELECTED" ?>>+/-
</select>
<br />Time window to display:<select name="lsrwindow">
 <option value="0" <?php if ($lsrwindow == 0) echo "SELECTED"; ?>>Hide
 <option value="5" <?php if ($lsrwindow == 5) echo "SELECTED"; ?>>5 minutes
 <option value="10" <?php if ($lsrwindow == 10) echo "SELECTED"; ?>>10 minutes
 <option value="15" <?php if ($lsrwindow == 15) echo "SELECTED"; ?>>15 minutes
 <option value="30" <?php if ($lsrwindow == 30) echo "SELECTED"; ?>>30 minutes
 <option value="60" <?php if ($lsrwindow == 60) echo "SELECTED"; ?>>60 minutes
</select>



