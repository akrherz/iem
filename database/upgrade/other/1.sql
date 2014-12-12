--
-- Storage of ISU FEEL Data
CREATE TABLE feel_data_daily(
	valid date UNIQUE,
	AirTemp_Max real,
	AirTemp_Min real,
	Rain_Tot real,
	Windspeed_Max real,
	SolarRad_MJ_Tot real
);
GRANT SELECT on feel_data_daily to nobody,apache;

CREATE TABLE feel_data_hourly(
	valid timestamptz UNIQUE,
	BattVolt_Avg real,
	PanTemp_Avg real,
	AirTemp_Avg real,
	RH_Avg real,
	sat_vp_Avg real,
	act_vp_Avg real,
	WindDir_Avg real,
	Windspeed_Avg real,
	SolarRad_mV_Avg real,
	SolarRad_W_Avg real,
	Soil_Temp_5_Avg real,
	Rain_Tot real,
	LWS1_Avg real,
	LWS2_Avg real,
	LWS3_Avg real,
	LWS1_Ohms real,
	LWS2_Ohms real,
	LWS3_Ohms real,
	LWS1_Ohms_Hst real,
	LWS2_Ohms_Hst real,
	LWS3_Ohms_Hst real
);
GRANT SELECT on feel_data_hourly to nobody,apache;
