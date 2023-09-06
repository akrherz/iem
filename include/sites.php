<?php
// Provides a context for PHP pages within the /sites/ IEM website
require_once dirname(__FILE__) . "/../config/settings.inc.php";
require_once dirname(__FILE__) . "/database.inc.php";
require_once dirname(__FILE__) . "/station.php";
require_once dirname(__FILE__) . "/forms.php";
require_once dirname(__FILE__) . "/myview.php";


class SitesContext
{
    public ?string $station = null;
    public ?string $network = null;
    public ?array $metadata = null;

    public function neighbors()
    {
        $con = iemdb("mesosite");
        $rs = pg_prepare($con, "_SELECT", "SELECT *,
         ST_distance(ST_transform(geom,3857), 
                     ST_transform(ST_Point({$this->metadata['lon']}, {$this->metadata['lat']}, 4326), 3857)) /1000.0 as dist from stations 
         WHERE ST_PointInsideCircle(geom, {$this->metadata['lon']}, {$this->metadata['lat']}, 0.25) 
         and id != $1 ORDER by dist ASC");
        $result = pg_execute($con, "_SELECT", array($this->station));

        $s = <<<EOM
<table class="table table-striped">
<thead class="sticky">
<tr><th>Distance [km]</th><th>Network</th><th>Station Name</th>
<th>Archive Start</th><th>Archive End</th></tr></thead>
<tbody>
EOM;
        for ($i = 0; $row = pg_fetch_assoc($result); $i++) {
            $s .= sprintf(
                "<tr><td>%.3f</td><td><a href=\"locate.php?network=%s\">%s</a></td>" .
                    "<td><a href=\"site.php?station=%s&network=%s\">%s</a></td>".
                    "<td>%s</td><td>%s</td></tr>",
                $row["dist"],
                $row["network"],
                $row["network"],
                $row["id"],
                $row["network"],
                $row["name"],
                $row["archive_begin"],
                $row["archive_end"],
            );
        }
        $s .= "</tbody></table>";
        return $s;
    }

    public function printtd($instr, $selected)
    {
        $s = "";
        $filename = "/mesonet/share/pics/{$this->station}/{$this->station}_$instr}.jpg";
        if (file_exists($filename)) {
            if ($instr == $selected) {
                $s .= '<td align="center" style="background: #ee0;">' . $instr . '</td>';
                $s .= "\n";
            } else {
                $s .= '<td align="center"><a href="pics.php?network=' . $this->network . '&station=' . $this->station . '&dir=' . $instr . '">' . $instr . '</a></td>';
                $s .= "\n";
            }
        } else {
            $s .= '<td align="center">' . $instr . '</td>';
            $s .= "\n";
        }
        return $s;
    }
}


function station_helper($station)
{
    // Attempt to help the user find this station
    $iemdb = iemdb("mesosite");
    $rs = pg_prepare($iemdb, "FIND", "SELECT id, name, network from stations " .
        "WHERE id = $1");
    $rs = pg_execute($iemdb, 'FIND', array($station));
    if (pg_num_rows($rs) == 0) {
        header("Location: locate.php");
        die();
    }
    $table = <<<EOF
    <p>Sorry, the requested station identifier and network could not be found
        within the IEM database.  Here are other network matches for your 
        identifier provided.</p>
    
    <table class="table table-ruled table-bordered">
    <thead><tr><th>ID</th><th>Name</th><th>Network</th></tr></thead>
    <tbody>
    EOF;
    while ($row = pg_fetch_assoc($rs)) {
        $table .= sprintf(
            "<tr><td>%s</td><td><a href=\"site.php?network=%s" .
                "&amp;station=%s\">%s</a></td><td>%s</td></tr>",
            $row["id"],
            $row["network"],
            $row["id"],
            $row["name"],
            $row["network"]
        );
    }
    $table .= "</tbody></table>";
    $t = new MyView();
    $t->title = "Sites";
    $t->content = $table;

    $t->render("single.phtml");
}

function get_sites_context()
{
    // Return a SitesContext
    $station = get_str404("station", "", 20);
    $network = get_str404("network", "", 14);  // could be 10?

    if ($station == "") {
        header("Location: /sites/locate.php");
        die();
    }

    $st = new StationData($station, $network);
    $cities = $st->table;
    if (!array_key_exists($station, $cities)) {
        station_helper($station);
        die();
    }

    if (!isset($_GET["network"])) {
        $network = $cities[$station]["network"];
    }
    $ctx = new SitesContext();
    $ctx->station = $station;
    $ctx->network = $network;
    $ctx->metadata = $cities[$station];
    return $ctx;
}
