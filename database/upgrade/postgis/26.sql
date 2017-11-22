-- Storage of Impact Text
ALTER TABLE riverpro add impact_text text;

CREATE OR REPLACE RULE replace_riverpro
 AS ON INSERT TO riverpro WHERE
 (EXISTS (SELECT 1 FROM riverpro
 WHERE ((riverpro.nwsli)::text = (new.nwsli)::text)))
 DO INSTEAD UPDATE riverpro SET stage_text = new.stage_text,
 flood_text = new.flood_text, forecast_text = new.forecast_text,
 severity = new.severity, impact_text = new.impact_text
 WHERE ((riverpro.nwsli)::text = (new.nwsli)::text);
 