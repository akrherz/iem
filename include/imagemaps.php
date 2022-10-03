<?php

function ugcStateSelect($state, $selected)
{
    $state = substr(strtoupper($state), 0, 2);
    include_once dirname(__FILE__) . "/database.inc.php";
    $dbconn = iemdb('postgis');
    $rs = pg_exec($dbconn, "SELECT ugc, name from ugcs WHERE end_ts is null "
        . " and substr(ugc,1,2) = '$state' ORDER by name ASC");
    $s = "<select name=\"ugc\">\n";
    for ($i = 0; $row = pg_fetch_array($rs); $i++) {
        $z = (substr($row["ugc"], 2, 1) == "Z") ? "Zone" : "County";
        $s .= "<option value=\"" . $row["ugc"] . "\" ";
        if ($row["ugc"] == $selected) {
            $s .= "SELECTED";
        }
        $s .= ">[" . $row["ugc"] . "] " . $row["name"] . " ($z)</option>\n";
    }
    return $s;
}


function selectAzosNetwork($network)
{
    $network = strtoupper($network);
    include_once dirname(__FILE__) . "/database.inc.php";
    $dbconn = iemdb('mesosite');
    $rs = pg_exec($dbconn, "SELECT * from networks WHERE id ~* 'ASOS' ORDER by name ASC");
    $s = "<select name=\"network\">\n";
    for ($i = 0; $row = pg_fetch_array($rs); $i++) {
        $s .= "<option value=\"" . $row["id"] . "\" ";
        if ($row["id"] == $network) {
            $s .= "SELECTED";
        }
        $s .= ">" . $row["name"] . "</option>\n";
    }
    return $s;
}

// Our climodat tracked networks
function selectClimodatNetwork($selected, $label = "network")
{
    $selected = strtoupper($selected);
    include_once dirname(__FILE__) . "/database.inc.php";
    $dbconn = iemdb('mesosite');
    $rs = pg_exec($dbconn, "SELECT * from networks " .
        "WHERE id ~* 'CLIMATE' ORDER by name ASC");
    $s = "<select class=\"iemselect2\" name=\"$label\">\n";
    for ($i = 0; $row = pg_fetch_array($rs); $i++) {
        $s .= "<option value=\"" . $row["id"] . "\" ";
        if ($row["id"] == $selected) {
            $s .= "SELECTED";
        }
        $s .= ">" . $row["name"] . "</option>\n";
    }
    return $s;
}

function selectNetwork($selected, $extra = array())
{
    $selected = strtoupper($selected);
    include_once dirname(__FILE__) . "/database.inc.php";
    $dbconn = iemdb('mesosite');
    $rs = pg_exec($dbconn, "SELECT * from networks ORDER by name ASC");
    $s = "<select class=\"iemselect2\" name=\"network\">\n";
    foreach ($extra as $idx => $sid) {
        $s .= "<option value=\"$idx\" ";
        if ($selected == $idx) {
            $s .= "SELECTED";
        }
        $s .= ">$sid</option>\n";
    }
    for ($i = 0; $row = pg_fetch_array($rs); $i++) {
        $s .= "<option value=\"" . $row["id"] . "\" ";
        if ($row["id"] == $selected) {
            $s .= "SELECTED";
        }
        $s .= ">" . $row["name"] . "</option>\n";
    }
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
    $s = "";
    include_once dirname(__FILE__) . "/network.php";
    $nt = new NetworkTable($network);
    $cities = $nt->table;
    $s .= "<select name=\"${label}\" size=\"5\" MULTIPLE >\n";

    foreach ($extra as $idx => $sid) {
        $s .= "<option value=\"$idx\" ";
        if ($selected == $idx) {
            $s .= "SELECTED";
        }
        $s .= ">[$idx] $sid </option>\n";
    }

    foreach ($cities as $sid => $tbl) {
        $s .= "<option value=\"$sid\" ";
        if ($selected == $sid) {
            $s .= "SELECTED";
        }
        $s .= ">[$sid] " . $tbl["name"] . "</option>\n";
    }
    $s .= "</select>\n";
    return $s;
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
    $only_online = FALSE
) {
    $s = "";
    include_once dirname(__FILE__) . "/network.php";
    $nt = new NetworkTable($network, FALSE, $only_online);
    $cities = $nt->table;
    $s .= "<select class=\"iemselect2\" name=\"$selectName\">\n";
    foreach ($cities as $sid => $tbl) {
        $s .= "<option value=\"$sid\" ";
        $sname = make_sname($tbl);
        if ($selected == $sid) {
            $s .= "SELECTED";
        }
        $s .= ">${sname}</option>\n";
    }
    foreach ($extra as $idx => $sid) {
        if (is_array($sid)) {
            $tbl = $sid;
            $sid = $idx;
        } else {
            $nt->load_station($sid);
            $tbl = $nt->table[$sid];
        }
        $sname = make_sname($tbl);
        $s .= "<option value=\"$sid\" ";
        if ($selected == $sid) {
            $s .= "SELECTED";
        }
        $s .= ">${sname}</option>\n";
    }
    $s .= "</select>\n";
    return $s;
}


function networkSelectAuto($network, $selected, $extra = array())
{
    $network = strtoupper($network);
    $s = "";
    include_once dirname(__FILE__) . "/network.php";
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
        $s .= ">${sname}</option>\n";
    }
    foreach ($extra as $idx => $sid) {
        $nt->load_station($sid);
        $tbl = $nt->table[$sid];
        $sname = make_sname($tbl);
        $s .= "<option value=\"$sid\" ";
        if ($selected == $sid) {
            $s .= "SELECTED";
        }
        $s .= ">${sname}</option>\n";
    }
    $s .= "</select>\n";
    return $s;
}


function isuagSelect($selected)
{
    $s = "";
    include_once dirname(__FILE__) . "/network.php";
    $nt = new NetworkTable("ISUAG");
    $cities = $nt->table;
    $s .= '<select name="station">\n';
    foreach ($cities as $sid => $tbl) {
        $s .= "<option value=\"$sid\" ";
        if ($selected == $sid) {
            $s .= "SELECTED";
        }
        $s .= ">" . $tbl["name"] . "</option>\n";
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
