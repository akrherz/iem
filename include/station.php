<?php
/* Build Network station tables on demand! */

require_once dirname(__FILE__) . "/network.php";


class StationData
{
    public $table;
    public $dbconn;
    public string $stname1;
    public string $stname2;

    public function __construct($a, $n = "")
    {
        $this->table = array();
        $dbconn = iemdb("mesosite");
        $sql_template = <<<EOM
    WITH attrs as (
        SELECT t.iemid, array_to_json(array_agg(a.attr)) as attrs,
        array_to_json(array_agg(a.value)) as attr_values
        from stations t LEFT JOIN station_attributes a
        on (t.iemid = a.iemid) WHERE %s
        GROUP by t.iemid)
    SELECT t.*, ST_X(t.geom) as lon, ST_Y(t.geom) as lat,
    a.attrs, a.attr_values from stations t JOIN attrs a on
    (t.iemid = a.iemid)
EOM;

        $this->stname1 = uniqid("s1");
        pg_prepare(
            $dbconn,
            $this->stname1,
            sprintf($sql_template, "id = $1 and network = $2")
        );
        $this->stname2 = uniqid("s2");
        pg_prepare(
            $dbconn,
            $this->stname2,
            sprintf($sql_template, "id = $1")
        );

        if (is_string($a)) {
            $this->loadStation($dbconn, $a, $n);
        } else if (is_array($a)) {
            foreach ($a as $id) {
                $this->loadStation($dbconn, $id, $n);
            }
        }
    }

    public function loadStation($dbconn, $id, $n = "")
    {
        if ($n != "") {
            $rs = pg_execute($dbconn, $this->stname1, array($id, $n));
        } else {
            $rs = pg_execute($dbconn, $this->stname2, array($id));
        }
        for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
            $this->table[$row["id"]] = $row;
            $this->doConversions($row["id"]);
        }
        if (pg_num_rows($rs) < 1) {
            return false;
        }
        return true;
    }

    public function doConversions($id)
    {
        if (!is_null($this->table[$id]["archive_begin"])) {
            $this->table[$id]["archive_begin"] = new DateTime($this->table[$id]["archive_begin"]);
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
