<?php
// Build Network station tables on demand!

require_once dirname(__FILE__) . "/database.inc.php";

class NetworkTable
{
    public array $table;
    public $dbconn;

    public function __construct($a, $force3char = FALSE, $only_online = FALSE)
    {
        $this->table = array();
        $ol = ($only_online) ? " and online = 't' " : "";
        $sql_template = <<<EOM
    WITH attrs as (
        SELECT t.iemid, array_to_json(array_agg(a.attr)) as attrs,
        array_to_json(array_agg(a.value)) as attr_values
        from stations t LEFT JOIN station_attributes a
        on (t.iemid = a.iemid) WHERE %s {$ol}
        GROUP by t.iemid)
    SELECT t.*, ST_X(t.geom) as lon, ST_Y(t.geom) as lat,
    a.attrs, a.attr_values from stations t JOIN attrs a on
    (t.iemid = a.iemid) ORDER by t.name ASC
EOM;
        // We force new here to prevent reused prepared statement names, hack
        $this->dbconn = iemdb("mesosite", PGSQL_CONNECT_FORCE_NEW);
        $rs = pg_prepare(
            $this->dbconn,
            "SELECT",
            sprintf($sql_template, "network = $1")
        );
        $rs = pg_prepare(
            $this->dbconn,
            "SELECTST",
            sprintf($sql_template, "id = $1")
        );
        if (is_string($a)) {
            $this->loadNetwork($a, $force3char);
        } else if (is_array($a)) {
            foreach ($a as $network) {
                $this->loadNetwork($network, $force3char);
            }
        }
    }

    public function loadNetwork($network, $force3char = FALSE)
    {
        $rs = pg_execute($this->dbconn, "SELECT", array($network));
        for ($i = 0; $row = pg_fetch_array($rs); $i++) {
            $keyid = $row["id"];
            if ($force3char && strlen($keyid) == 4) {
                $keyid = substr($keyid, 1, 3);
            }
            $this->table[$keyid] = $row;
            $this->do_conversions($keyid);
        }
    }

    public function loadStation($id)
    {
        $rs = pg_execute($this->dbconn, "SELECTST", array($id));
        for ($i = 0; $row = pg_fetch_array($rs); $i++) {
            $this->table[$row["id"]] = $row;
            $this->do_conversions($row["id"]);
        }
        if (pg_num_rows($rs) < 1) {
            return false;
        }
        return true;
    }

    public function do_conversions($id)
    {
        if (!is_null($this->table[$id]["archive_begin"])) {
            // can't deal with ancient dates
            $this->table[$id]["archive_begin"] = new DateTime(
                substr($this->table[$id]["archive_begin"], 0, 10)
            );
        }
        if (!is_null($this->table[$id]["archive_end"])) {
            $this->table[$id]["archive_end"] = new DateTime($this->table[$id]["archive_end"]);
        }
        // Make attributes more accessible
        $this->table[$id]["attrs"] = json_decode($this->table[$id]["attrs"]);
        $this->table[$id]["attr_values"] = json_decode($this->table[$id]["attr_values"]);
        $this->table[$id]["attributes"] = array();
        foreach ($this->table[$id]["attrs"] as $key => $value) {
            $this->table[$id]["attributes"][$value] = $this->table[$id]["attr_values"][$key];
        }
    }

    public function get($id)
    {
        return $this->table[$id];
    }
}
