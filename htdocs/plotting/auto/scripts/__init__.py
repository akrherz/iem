"""
Examples of widget types

dict(type='date', name='date2', default='2012/03/15', label='Bogus2:',
     min="1893/01/01"), # Comes back to python as yyyy-mm-dd

>>> res = list(range(230))
>>> for key in scripts.data:
...   for entry in scripts.data[key]:
...     for opt in entry['options']:
...       if opt["id"] in res:
...         res.remove(opt["id"])
...
>>> res

Not listed due to having no PNG output
111, 112, 114, 115, 117, 118, 121, 122, 123, 124, 141, 143

"""
# Association of plots
daily_opts = [
    {
        "id": 51,
        "label": (
            "Accumulated Station Departures of Precip/GDD/SDD "
            "(Automated Stations)"
        ),
    },
    {
        "id": 108,
        "label": (
            "Accumulated Station Departures of Precip/GDD/SDD "
            "(Long Term Climate)"
        ),
    },
    {
        "id": 172,
        "label": "Accumulated Year to Date / Period Precipitation / Snowfall",
    },
    {
        "id": 149,
        "label": "Aridity Index (High Temperature minus Precip Departures)",
    },
    {
        "id": 11,
        "label": (
            "ASOS Daily Min/Max Dew Point/Temp/Feels Like/RH " "for a Year"
        ),
    },
    {"id": 94, "label": "Bias of 24 Hour High+Low Computation by Hour"},
    {"id": 96, "label": "Bias of 24 Hour Precipitation Computation by Hour"},
    {
        "id": 82,
        "label": "Calendar of Daily Observations from Automated Stations",
    },
    {"id": 218, "label": "Daily NWS CLImate Report Infographic"},
    {"id": 180, "label": "Daily Temperature/Precip/Snowfall Climatology"},
    {
        "id": 32,
        "label": "Daily Temperature Departures / Percentiles for One Year",
    },
    {
        "id": 21,
        "label": "Change in NCEI 1991-2020 Daily Climatology over X Days",
    },
    {"id": 174, "label": "Compare Daily High/Low Temps for ASOS Stations"},
    {
        "id": 215,
        "label": (
            "Compare Daily High/Low Temps Distributions "
            "over Two Periods of Years"
        ),
    },
    {
        "id": 91,
        "label": "Consecutive Day Statistics of High+Low Temps / Precip",
    },
    {
        "id": 66,
        "label": (
            "Consecutive Days Frequency by DOY for High/Low Temp "
            "Above/Below Threshold"
        ),
    },
    {
        "id": 216,
        "label": (
            "Consecutive Days by Year with High/Low Temp "
            "Above/Below Threshold"
        ),
    },
    {
        "id": 9,
        "label": (
            "Cooling/Growing/Heating/Stress Degree Day "
            "Daily Values and Climatology"
        ),
    },
    {
        "id": 49,
        "label": (
            "Daily/Multi-Day Frequency of Some Threshold "
            "(snow, precip, temps)"
        ),
    },
    {"id": 113, "label": "Daily Climatology"},
    {"id": 176, "label": "Daily/Monthly/Yearly Records Beat Margin"},
    {"id": 5, "label": "Daily Records for each month of year"},
    {
        "id": 31,
        "label": "Extreme Jumps or Dips in High/Low Temperature over X days",
    },
    {
        "id": 147,
        "label": "Frequency of One Station Warmer/Wetter than Another",
    },
    {
        "id": 205,
        "label": (
            "Frequency of Daily Summary Variables for Automated Stations"
        ),
    },
    {
        "id": 7,
        "label": "Growing Degree Day Periods for One Year by Planting Date",
    },
    {
        "id": 204,
        "label": "Heatmap of Daily / Trailing Daily Temperature / Precip",
    },
    {
        "id": 225,
        "label": "Heatmap of Distribution of Trailing Departures",
    },
    {
        "id": 61,
        "label": (
            "High/Low Temp above/below avg OR dry streaks by NWS CLI Sites"
        ),
    },
    {"id": 19, "label": "Histogram of Daily High/Low Temperatures + Ranges"},
    {"id": 35, "label": "Histogram of X Hour Temp/RH/Dew/Pressure Changes"},
    {
        "id": 60,
        "label": ("Hourly Variable Frequencies/Min/Max by Week of Year"),
    },
    {"id": 86, "label": "IEM Daily Reanalysis Plots"},
    {
        "id": 139,
        "label": (
            "Largest / Smallest Local Calendar Day Temperature Differences"
        ),
    },
    {"id": 168, "label": "Latest Date of Year for High Temperature"},
    {"id": 229, "label": "Lightning Flash Density Maps"},
    {"id": 207, "label": "Local Storm Report + COOP Snowfall Analysis Maps"},
    {"id": 206, "label": "Map of Daily Automated Station Summaries"},
    {"id": 97, "label": "Map of Departures/Stats over One Period of Days"},
    {
        "id": 34,
        "label": (
            "Max Stretch of Days with High/Low Above/Below "
            "Threshold or Climatology"
        ),
    },
    {
        "id": 26,
        "label": "Min Daily Low after 1 July / Max Daily High for year",
    },
    {
        "id": 126,
        "label": (
            "Mixing Ratio / Vapor Pressure Deficit Climatology "
            "and Yearly Timeseries Plot"
        ),
    },
    {
        "id": 84,
        "label": (
            "MRMS Q3 / PRISM / Stage IV / IFC / IEM Reanalysis Estimated "
            "Precipitation (multiday summaries/departures)"
        ),
    },
    {
        "id": 185,
        "label": (
            "Number of Days to Accumulate an Amount of Precipitation (MRMS)"
        ),
    },
    {
        "id": 164,
        "label": (
            "Percentage of NWS CLI Sites Reporting Daily Above/Below "
            "Temps or Precip/Snow"
        ),
    },
    {
        "id": 22,
        "label": (
            "Percentage of Years within Temperature Range from Averages"
        ),
    },
    {
        "id": 83,
        "label": (
            "Period Averages or Totals of X days around a "
            "given day of the year"
        ),
    },
    {
        "id": 140,
        "label": (
            "Period Statistics of Temp/Precip/Wind for a date period "
            "each year [ASOS/Automated Stations]"
        ),
    },
    {
        "id": 107,
        "label": (
            "Period Statistics of Temp/Precip for a date period "
            "each year [COOP/Climate Sites]"
        ),
    },
    {
        "id": 182,
        "label": "Precipitation (MRMS) Coverage Efficiency by State",
    },
    {
        "id": 110,
        "label": "Precipitation Frequency Bins by Climate Week (climodat)",
    },
    {"id": 43, "label": "Recent (Past 2-3 Days) Timeseries (Meteogram)"},
    {"id": 157, "label": "Relative Humidity Max/Min/Avg by Day of Year"},
    {"id": 62, "label": "Snow Depth"},
    {"id": 199, "label": "ISU Soil Moisture Network Daily Plots"},
    {"id": 38, "label": "Solar Radiation Estimates from NARR"},
    {"id": 25, "label": "Spread of Daily High and Low Temperatures"},
    {"id": 137, "label": "Start Date of Spring/Fall with Statistics"},
    {
        "id": 4,
        "label": "State Areal Coverage of Precip Intensity over X Days",
    },
    {"id": 89, "label": "State Areal Coverage/Efficiency of Precipitation"},
    {"id": 81, "label": "Standard Deviation of Daily Temperatures"},
    {"id": 28, "label": "Trailing Number of Days Precipitation Total Rank"},
    {
        "id": 228,
        "label": "Trailing Standardized Precipitation (SPI) + Drought Monitor",
    },
    {
        "id": 142,
        "label": "Trailing X Number of Days Temp/Precipitation Departures",
    },
    {"id": 132, "label": "Top 10 Precip/Temperature Values by Month/Season"},
    {"id": 190, "label": "Year of Daily High/Low Temperature Record"},
]
monthly_opts = [
    {
        "id": 130,
        "label": "Average High/Low Temperature with/without Snowcover",
    },
    {"id": 125, "label": "Climatological Maps of Period Averages"},
    {"id": 1, "label": "Comparison of Multi-Month Totals/Averages"},
    {"id": 55, "label": "Daily Climatology Comparison"},
    {"id": 17, "label": "Daily High/Low Temps or Precip with Climatology"},
    {
        "id": 129,
        "label": "Daily Observation Percentiles/Frequencies by Month",
    },
    {"id": 15, "label": "Daily Temperature Change Frequencies by Month"},
    {
        "id": 98,
        "label": "Day of Month Frequency of meeting temp/precip threshold",
    },
    {
        "id": 65,
        "label": "Day of the Month with the coldest/warmest temperature",
    },
    {"id": 161, "label": "Days per month/season above/below some threshold"},
    {
        "id": 29,
        "label": "Frequency of Hourly Temperature within Range by Month",
    },
    {"id": 116, "label": ("Cooling/Heating Degree Days monthly totals")},
    {
        "id": 42,
        "label": "Consecutive Hours / Streaks Above/Below Threshold",
    },
    {"id": 154, "label": "Hourly Temperature Averages by Month"},
    {"id": 85, "label": "Hourly Temperature Frequencies by Month"},
    {"id": 20, "label": "Hours of Precipitation by Month"},
    {"id": 177, "label": "ISU Soil Moisture Network Timeseries Plots"},
    {
        "id": 2,
        "label": "Month Precipitation vs Month Growing Degree Day Departures",
    },
    {
        "id": 223,
        "label": "Monthly/Seasonal Partition of Temperature/Precip Reports",
    },
    {
        "id": 57,
        "label": "Monthly Precipitation/Temperature Records or Climatology",
    },
    {
        "id": 95,
        "label": "Monthly Precipitation/Temperature with El Nino SOI Index",
    },
    {
        "id": 24,
        "label": (
            "Monthly Precipitation/Temperature "
            "Climate District / Statewide Ranks/Aridity"
        ),
    },
    {
        "id": 3,
        "label": "Monthly Precipitation/Temperature Statistics by Year",
    },
    {"id": 6, "label": "Monthly Precipitation/Temperature Distributions"},
    {"id": 8, "label": "Monthly Precipitation Reliability"},
    {"id": 23, "label": "Monthly Station Departures + El Nino 3.4 Index"},
    {"id": 36, "label": "Month warmer than other Month for Year"},
    {
        "id": 58,
        "label": (
            "One Day's Precipitation Greater than X percentage "
            "of Monthly Total"
        ),
    },
    {
        "id": 41,
        "label": (
            "Quantile / Quantile Plot of Daily Temperatures "
            "for Two Months/Periods"
        ),
    },
    {"id": 47, "label": "Snowfall vs Precipitation Total for a Month"},
    {
        "id": 39,
        "label": "Scenarios for this month besting some previous month",
    },
    {
        "id": 71,
        "label": "Wind Speed and Wind Direction Daily Averages for Month",
    },
    {
        "id": 138,
        "label": "Wind Speed and Wind Direction Monthly Climatology",
    },
    {"id": 173, "label": "Wind Speed Hourly Climatology by Month or Period"},
]
yearly_opts = [
    {
        "id": 135,
        "label": "Accumulated Days with High/Low Above/Below Threshold",
    },
    {
        "id": 76,
        "label": (
            "Dew Point / Vapor Pressure Deficit / RH Distributions "
            "by Year or Season"
        ),
    },
    {"id": 125, "label": "Climatological Maps of Annual/Monthly Averages"},
    {
        "id": 151,
        "label": (
            "Difference between two periods or single period of years [map]"
        ),
    },
    {
        "id": 187,
        "label": "Compare one station yearly summary vs entire state",
    },
    {
        "id": 128,
        "label": "Comparison of Yearly Summaries between two stations",
    },
    {"id": 99, "label": "Daily High + Low Temperatures with Departures"},
    {
        "id": 12,
        "label": (
            "Days per year and first/latest date "
            "above/below given threshold"
        ),
    },
    {
        "id": 184,
        "label": (
            "Days per year with High Temperature "
            "above temperature thresholds"
        ),
    },
    {
        "id": 74,
        "label": (
            "Days per year by season or year with temperature "
            "above/below threshold"
        ),
    },
    {
        "id": 181,
        "label": ("Days per year with temp/precip/snowfall within ranges"),
    },
    {
        "id": 13,
        "label": "End/Start Date of Summer (warmest 91 day period) per Year",
    },
    {
        "id": 27,
        "label": "First Fall Temp Below Threshold (First Freeze/Frost)",
    },
    {"id": 165, "label": "First / Last Date of Temperature Threshold [map]"},
    {
        "id": 119,
        "label": "Frequency of First Fall High/Low Temperature by Day of Year",
    },
    {
        "id": 120,
        "label": (
            "Frequency of Last Spring High/Low Temperature by Day of Year"
        ),
    },
    {"id": 189, "label": ("General yearly totals with trend line fitted")},
    {"id": 179, "label": ("Growing Degree Day Scenarios For This Year")},
    {
        "id": 152,
        "label": ("Growing Season Differences Map between Two Periods"),
    },
    {
        "id": 148,
        "label": "Holiday or Same Day Daily Weather Observations each year",
    },
    {
        "id": 53,
        "label": ("Hourly Frequency of Temperature within Certain Ranges"),
    },
    {
        "id": 10,
        "label": (
            "Last Spring and First Fall Date above/below given threshold"
        ),
    },
    {"id": 64, "label": "Last or First Snowfall of Each Winter Season"},
    {"id": 33, "label": "Maximum Low Temperature Drop"},
    {
        "id": 188,
        "label": (
            "Max/Min High/Low after first temperature exceedence of season"
        ),
    },
    {"id": 105, "label": "Maximum Period between Precipitation Amounts"},
    {"id": 46, "label": "Minimum Wind Chill / Max Heat Index Temperature"},
    {"id": 30, "label": "Monthly Temperature Range"},
    {"id": 44, "label": "NWS Office Accumulated SVR+TOR Warnings"},
    {"id": 69, "label": "Percentage of Days each Year Above/Below Average"},
    {
        "id": 77,
        "label": "Period between Last and First High Temperature for Year",
    },
    {
        "id": 134,
        "label": "Period each year that was warmest/coldest/wettest",
    },
    {"id": 75, "label": "Precipitation Totals by Season/Year"},
    {
        "id": 63,
        "label": "Records Set by Year (Max High / Min Low / Max Precip)",
    },
    {
        "id": 144,
        "label": "Soil Temperature Periods Above/Below Threshold in Spring",
    },
    {
        "id": 145,
        "label": "Soil Temperature / Moisture Daily Time Series by Year",
    },
    {
        "id": 175,
        "label": "Snow Coverage Percentage for State For One Winter",
    },
    {
        "id": 133,
        "label": "Snowfall Season Totals Split by Date within Season",
    },
    {
        "id": 103,
        "label": "Step Ups in High Temp / Step Downs in Low Temp by Year",
    },
    {"id": 100, "label": "Temperature / Precipitation Statistics by Year"},
    {
        "id": 136,
        "label": "Time per Winter Season below Wind Chill Threshold",
    },
    {
        "id": 104,
        "label": "Trailing X day temp/precip departures (weather cycling)",
    },
    {
        "id": 14,
        "label": "Yearly Precipitation Contributions by Daily Totals",
    },
]
hopts = [
    {
        "id": 160,
        "label": ("River Gauge Obs and Forecasts from HML Products"),
    },
    {"id": 178, "label": ("NWS RFC Flash Flood Guidance Plots")},
    {"id": 183, "label": ("US Drought Monitor Areal Coverage by State")},
    {
        "id": 186,
        "label": ("US Drought Monitor Change in Areal Coverage by State"),
    },
    {
        "id": 194,
        "label": ("US Drought Monitor Time Duration over Period Maps"),
    },
    {
        "id": 193,
        "label": (
            "US Drought Monitor + Weather Prediction Center Forecasted Rain"
        ),
    },
]
mopts = [
    {
        "id": 78,
        "label": (
            "Average Dew Point/RH% by Air Temperature "
            "by Month or Season or Year"
        ),
    },
    {
        "id": 79,
        "label": (
            "Average Dew Point by Wind Direction by Month or Season or Year"
        ),
    },
    {
        "id": 40,
        "label": (
            "Cloud Amount and Level Timeseries / Visibility for One Month"
        ),
    },
    {"id": 88, "label": "Cloudiness Impact on Hourly Temperatures"},
    {"id": 214, "label": "Combos of Hourly Observations Var Vs Var"},
    {"id": 59, "label": "Daily u and vs Wind Component Climatologies"},
    {
        "id": 54,
        "label": (
            "Difference between morning low "
            "or afternoon high temperature between two sites"
        ),
    },
    {
        "id": 167,
        "label": (
            "Flight / Aviation Condition (VFR, MVFR, IFR, LIFR) "
            "hourly for one month"
        ),
    },
    {
        "id": 87,
        "label": (
            "Frequency of METAR Code (Thunder, etc) by week or day by hour"
        ),
    },
    {
        "id": 131,
        "label": (
            "Frequency of Overcast Clouds / Clear Skies "
            "by Air Temperature by month/season"
        ),
    },
    {
        "id": 93,
        "label": (
            "Heat Index / Temperature / Dew Point / "
            "Wind Chill Hourly Histogram"
        ),
    },
    {"id": 192, "label": "Hourly Analysis Maps of ASOS/METAR Stations"},
    {"id": 153, "label": "Hourly Extremes by Month/Season/Year"},
    {
        "id": 159,
        "label": "Hourly Frequency / Histogram by year and by hour of day",
    },
    {
        "id": 106,
        "label": "Hourly temp distributions on days exceeding temperature",
    },
    {
        "id": 202,
        "label": "Hourly variable comparison between two hours on one day",
    },
    {"id": 169, "label": "Largest Rise/Drop in Temperature over X Hours"},
    {"id": 18, "label": "Long term observation time series"},
    {"id": 45, "label": "Monthly Frequency of Overcast Conditions"},
    {
        "id": 170,
        "label": "Monthly Frequency of Present Weather Code in METAR Report",
    },
    {
        "id": 67,
        "label": "Monthly Frequency of Wind Speeds by Air Temperature",
    },
    {"id": 37, "label": "MOS Forecast Ranges + ASOS Observations"},
    {"id": 211, "label": "One Minute Interval Plots"},
    {"id": 222, "label": "One Minute Precipitation During Severe Weather"},
    {
        "id": 162,
        "label": "Overcast Sky Condition 2D Histogram (Level by Week)",
    },
    {
        "id": 213,
        "label": (
            "Percentiles of Hourly ASOS Data by Day, Week, Month, or Year"
        ),
    },
    {
        "id": 146,
        "label": "Temperature Frequency by Week During Precipitation",
    },
    {
        "id": 155,
        "label": ("Top 10 / Most Recent Hourly Reports from ASOS Stations"),
    },
    {"id": 16, "label": "Wind Rose when specified criterion is meet"},
]
nsopts = [
    {"id": 156, "label": "NASS Crop Condition by Year for Six States"},
    {"id": 127, "label": "NASS Crop Progress by Year"},
    {"id": 197, "label": "NASS Crop Progress State Average Map"},
    {"id": 209, "label": "NASS Crop Progress Weekly Change"},
]
nopts = [
    {
        "id": 196,
        "label": (
            "ASOS/METAR Heat Index / Wind Chill Frequencies by "
            "NWS Alert Headline"
        ),
    },
    {
        "id": 191,
        "label": "Calendar Plot of Watch/Warn/Adv Daily Counts",
    },
    {"id": 92, "label": "Days since Last Watch/Warning/Advisory by WFO"},
    {
        "id": 72,
        "label": "Frequency of Watch/Warning/Advisories by Time of Day",
    },
    {
        "id": 50,
        "label": (
            "Frequency of Hail/Wind Tags used in Severe TStorm Warnings"
        ),
    },
    {
        "id": 52,
        "label": "Gantt Chart of WFO Issued Watch/Warning/Advisories",
    },
    {"id": 163, "label": "Local Storm Reports Issued by WFO/State [map]"},
    {"id": 102, "label": "Local Storm Report Source Type Ranks by Year"},
    {
        "id": 44,
        "label": "NWS Office Accumulated Watch/Warning/Advisories by Year",
    },
    {
        "id": 68,
        "label": "Number of Distinct Phenomena/Significance VTEC per Year",
    },
    {
        "id": 73,
        "label": "Number of Watch/Warning/Advisories Issued per Year",
    },
    {
        "id": 171,
        "label": (
            "Number of Watch/Warning/Advisories Issued per Year per Month"
        ),
    },
    {
        "id": 70,
        "label": "Period between First and Last VTEC Product Each Year",
    },
    {
        "id": 224,
        "label": "Population under NWS Watch/Warning/Advisory at Time",
    },
    {"id": 203, "label": "Storm Based Warning Polygon Visual Summary"},
    {"id": 195, "label": "Storm Motion distribution based on NWS Warnings"},
    {
        "id": 201,
        "label": (
            "SPC Convective/Fire Wx or "
            "WPC Excessive Rainfall Outlook Calendar"
        ),
    },
    {
        "id": 230,
        "label": (
            "SPC Convective/Fire Wx or "
            "WPC Excessive Rainfall Last Event Infographic"
        ),
    },
    {"id": 200, "label": "SPC + WPC Outlook Heatmap"},
    {
        "id": 166,
        "label": (
            "Storm Prediction Center (SPC) Watches per Year for a State"
        ),
    },
    {"id": 210, "label": "Text Product Frequency Maps"},
    {"id": 48, "label": "Time of Day Frequency for Given Warning / UGC"},
    {
        "id": 80,
        "label": "Time Duration of a Watch/Warning/Advisory for a UGC",
    },
    {"id": 101, "label": "Top 25 Most Frequent VTEC Products by Office/NWS"},
    {
        "id": 56,
        "label": "Weekly/Daily/Monthly Frequency of a Watch/Warning/Advisory",
    },
    {
        "id": 109,
        "label": (
            "WFO / State VTEC Event Counts/Time Coverage Percent/Num Days "
            "for a Given Period (map)"
        ),
    },
    {"id": 208, "label": ("WFO VTEC Single Event Map Plot (map)")},
    {
        "id": 90,
        "label": (
            "UGC or Polygon SBW Statistics for "
            "Watch/Warning/Advisory by state/wfo"
        ),
    },
]
topts = [{"id": 158, "label": "Tall Towers - 1 Second Interval Time Series "}]
uopts = [
    {
        "id": 198,
        "label": (
            "Monthly Max/Min/Avgs for Sounding Parameter "
            "or Variable at Given Level"
        ),
    },
    {
        "id": 150,
        "label": ("Single Sounding Mandatory Level Percentile Ranks"),
    },
    {"id": 212, "label": "Sounding Parameter / Variable Yearly Timeseries"},
]
misc = [
    {"id": 226, "label": "Center Weather Advisory (CWA) Map"},
    {"id": 221, "label": "HRRR Time-Lagged Ensemble Reflectivity Plot"},
    {"id": 227, "label": "NWEM / NWS Non-VTEC Products containing a polygon"},
    {"id": 220, "label": "SPC Convective / Fire Weather Outlook Graphics"},
    {"id": 217, "label": "SPS Special Weather Statement Maps"},
    {"id": 219, "label": "Terminal Aerodome Forecast (TAF) Infographic"},
]
data = {
    "plots": [
        {"label": "Daily", "options": daily_opts},
        {"label": "Monthly", "options": monthly_opts},
        {"label": "Yearly", "options": yearly_opts},
        {"label": "Hydrology / Drought Monitor Plots", "options": hopts},
        {"label": "METAR ASOS Special Plots", "options": mopts},
        {"label": "NASS Quickstats (USDA Crop Statistics)", "options": nsopts},
        {"label": "NWS Warning Plots", "options": nopts},
        {"label": "Tall Towers Plots", "options": topts},
        {"label": "Upper Air / RAOB Sounding Plots", "options": uopts},
        {"label": "Miscellaneous", "options": misc},
    ]
}
