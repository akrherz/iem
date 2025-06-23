/* global Tabulator */

document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('thetable');
    if (table) {
        new Tabulator('#thetable', {
            layout: 'fitColumns',
            responsiveLayout: 'collapse',
            columns: [
                {title: "ID:", field: "id"},
                {title: "Location:", field: "location", formatter: "html"},
                {title: "High:", field: "high"},
                {title: "Low:", field: "low"},
                {title: "Min Feels Like[F]:", field: "min_feels"},
                {title: "Max Feels Like [F]:", field: "max_feels"},
                {title: "Min Dew Point [F]:", field: "min_dew"},
                {title: "Max Dew Point [F]:", field: "max_dew"},
                {title: "Rainfall:", field: "rainfall"},
                {title: "Peak Gust:", field: "peak_gust"},
                {title: "Time of Gust:", field: "gust_time"},
                {title: "Snowfall:", field: "snowfall"},
                {title: "Snow Depth:", field: "snow_depth"}
            ]
        });
    }
});