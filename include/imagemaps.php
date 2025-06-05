<?php
require_once dirname(__FILE__) . "/database.inc.php";
require_once dirname(__FILE__) . "/network.php";

/**
 * Convert a vague 3 character WFO identifier to a 4 character one
 * @param wfo3 the 3 character WFO identifier
 * @return the 4 character WFO identifier
 */
function rectify_wfo($wfo3){
    $xref = Array(
        "AFC" => "PAFC",
        "AJK" => "PAJK",
        "AFG" => "PAFG",
        "HFO" => "PHFO",
        "GUM" => "PGUM",
        "SJU" => "TJSJ",
        "JSJ" => "TJSJ",
    );
    if (array_key_exists($wfo3, $xref)){
        return $xref[$wfo3];
    };
    return sprintf("K%s", $wfo3);
}

/**
 * Figure out the vague 3 character ID :/
 * @param wfo3 the 3 character WFO identifier
 * @return the 4 character WFO identifier
 */
function unrectify_wfo($wfo){
    if (strlen($wfo) == 4){
        $wfo = substr($wfo, 1, 3);
    }
    if ($wfo == "SJU"){
        return "JSJ";
    }
    return $wfo;
}


function ugcStateSelect($state, $selected)
{
    $state = substr(strtoupper($state), 0, 2);
    $dbconn = iemdb('postgis');
    $stname = iem_pg_prepare($dbconn, "SELECT ugc, name from ugcs WHERE end_ts is null "
        . " and substr(ugc,1,2) = $1 ORDER by name ASC");
    $rs = pg_execute($dbconn, $stname, array($state));
    $s = "<select name=\"ugc\">\n";
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        $z = (substr($row["ugc"], 2, 1) == "Z") ? "Zone" : "County";
        $s .= "<option value=\"" . $row["ugc"] . "\" ";
        if ($row["ugc"] == $selected) {
            $s .= "SELECTED";
        }
        $s .= ">[" . $row["ugc"] . "] " . $row["name"] . " ($z)</option>\n";
    }
    $s .= "</select>\n";
    return $s;
}


/**
 * Select a network type
 * @param nettype the network type
 * @param selected the selected network id
 * @return the select box
 */
function selectNetworkType($nettype, $selected)
{
    $selected = strtoupper($selected);
    $dbconn = iemdb('mesosite');
    $stname = iem_pg_prepare(
        $dbconn,
        "SELECT * from networks WHERE id ~* $1 ORDER by name ASC");
    $rs = pg_execute($dbconn, $stname, array($nettype));
    $s = "<select class=\"iemselect2\" name=\"network\">\n";
    while ($row = pg_fetch_assoc($rs)) {
        $s .= "<option value=\"" . $row["id"] . "\" ";
        if ($row["id"] == $selected) {
            $s .= "SELECTED";
        }
        $s .= ">" . $row["name"] . "</option>\n";
    }
    $s .= "</select>\n";
    return $s;
}


function selectNetwork($selected, $extra = array())
{
    $selected = strtoupper($selected);
    $dbconn = iemdb('mesosite');
    $rs = pg_exec($dbconn, "SELECT * from networks ORDER by name ASC");
    $s = "<select class=\"iemselect2\" name=\"network\">\n";
    foreach ($extra as $idx => $sid) {
        $s .= "<option value=\"$idx\" ";
        if ($selected == $idx) {
            $s .= "SELECTED";
        }
        $s .= ">[{$idx}] {$sid}</option>\n";
    }
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        $s .= "<option value=\"" . $row["id"] . "\" ";
        if ($row["id"] == $selected) {
            $s .= "SELECTED";
        }
        $s .= ">[{$row['id']}] {$row['name']}</option>\n";
    }
    $s .= "</select>\n";
    return $s;
}

/*
 * Generate a select box that allows multiple selections!
 * @param extra is an array of extra values for this box
 */
function networkMultiSelect(
    $network,
    $selected,
    $extra = array(),
    $label = "station"
) {
    $nt = new NetworkTable($network);
    
    // Create DOM document
    $dom = new DOMDocument('1.0', 'UTF-8');
    $dom->formatOutput = false; // Keep compact for web output
    
    // Create select element
    $select = $dom->createElement('select');
    $select->setAttribute('name', $label);
    $select->setAttribute('size', '5');
    $select->setAttribute('multiple', 'multiple');

    // Add extra options first
    foreach ($extra as $idx => $sid) {
        $option = $dom->createElement('option');
        $option->setAttribute('value', $idx);
        $option->textContent = "[$idx] $sid";
        
        if ($selected == $idx) {
            $option->setAttribute('selected', 'selected');
        }
        
        $select->appendChild($option);
    }

    // Add options from network table
    foreach ($nt->table as $sid => $tbl) {
        $option = $dom->createElement('option');
        $option->setAttribute('value', $sid);
        $option->textContent = "[$sid] " . $tbl["name"];
        
        if ($selected == $sid) {
            $option->setAttribute('selected', 'selected');
        }
        
        $select->appendChild($option);
    }
    
    $dom->appendChild($select);
    return $dom->saveHTML($select);
}

function make_sname($tbl)
{
    // Construct a nice label for the given station
    $dextra = '';
    if (!is_null($tbl['archive_begin'])) {
        $dextra .= sprintf(" [%s-", $tbl["archive_begin"]->format("Y"));
        if (!is_null($tbl['archive_end'])) {
            $dextra .= $tbl["archive_end"]->format("Y");
        }
        $dextra .= "]";
    }
    return sprintf("[%s] %s%s", $tbl['id'], $tbl['name'], $dextra);
}

function networkSelect(
    $network,
    $selected,
    $extra = array(),
    $selectName = "station",
    $only_online = FALSE,
    $clsname = "iemselect2"
) {
    $nt = new NetworkTable($network, FALSE, $only_online);
    
    // Create DOM document
    $dom = new DOMDocument('1.0', 'UTF-8');
    $dom->formatOutput = false; // Keep compact for web output
    
    // Create select element
    $select = $dom->createElement('select');
    $select->setAttribute('name', $selectName);
    $select->setAttribute('class', $clsname);
    
    // Add options from network table
    foreach ($nt->table as $sid => $tbl) {
        $option = $dom->createElement('option');
        $option->setAttribute('value', $sid);
        $option->textContent = make_sname($tbl);
        
        if ($selected === $sid) {
            $option->setAttribute('selected', 'selected');
        }
        
        $select->appendChild($option);
    }
    
    // Add extra options
    foreach ($extra as $idx => $sid) {
        if (is_array($sid)) {
            $tbl = $sid;
            $sid = $idx;
        } else {
            $nt->loadStation($sid);
            $tbl = $nt->table[$sid];
        }
        
        $option = $dom->createElement('option');
        $option->setAttribute('value', $sid);
        $option->textContent = make_sname($tbl);
        
        if ($selected === $sid) {
            $option->setAttribute('selected', 'selected');
        }
        
        $select->appendChild($option);
    }
    
    $dom->appendChild($select);
    return $dom->saveHTML($select);
}


function networkSelectAuto($network, $selected, $extra = array())
{
    $network = strtoupper($network);
    $s = "";
    $nt = new NetworkTable($network);
    $cities = $nt->table;
    $s .= "<select class=\"iemselect2\" name=\"station\" onChange=\"this.form.submit()\">\n";
    foreach ($cities as $sid => $tbl) {
        $sname = make_sname($tbl);
        if ($tbl["network"] != $network) continue;
        $s .= "<option value=\"$sid\" ";
        if ($selected == $sid) {
            $s .= "SELECTED";
        }
        $s .= ">{$sname}</option>\n";
    }
    foreach ($extra as $idx => $sid) {
        $nt->loadStation($sid);
        $tbl = $nt->table[$sid];
        $sname = make_sname($tbl);
        $s .= "<option value=\"$sid\" ";
        if ($selected == $sid) {
            $s .= "SELECTED";
        }
        $s .= ">{$sname}</option>\n";
    }
    $s .= "</select>\n";
    return $s;
}

function rwisMultiSelect($selected, $size)
{
    include_once dirname(__FILE__) . "/network.php";
    $nt = new NetworkTable("IA_RWIS");
    $cities = $nt->table;
    $s = "<select name=\"stations\" size=\"" . $size . "\" MULTIPLE>\n";
    $s .= "<option value=\"_ALL\">Select All</option>\n";
    foreach ($cities as $key => $val) {
        if ($val["network"] != "IA_RWIS") continue;
        $s .= "<option value=\"" . $key . "\"";
        if ($selected == $key) {
            $s .= " SELECTED ";
        }
        $s .= " >" . $val["name"] . " (" . $key . ")\n";
    }

    $s .= "</select>\n";
    return $s;
}
