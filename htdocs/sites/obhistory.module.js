import { requireElement } from '/js/iemjs/domUtils.js';
let station = null;
let network = null;
let metar_show = false;
let madis_show = false;

function updateURI() {
    // Build URI with modern date parameter and current settings
    const datePicker = requireElement("date_picker");
    const sortDirElement = document.querySelector('select[name="sortdir"]');
    const windUnitsElement = document.querySelector('select[name="windunits"]');
    const sortDir = sortDirElement ? sortDirElement.value : "asc";
    const windUnits = windUnitsElement ? windUnitsElement.value : "mph";
    const currentDate = datePicker.value;
    let uri = `${window.location.origin}${window.location.pathname}?`+
        `station=${station}&network=${network}&date=${currentDate}&sortdir=${sortDir}&windunits=${windUnits}`;
    if (metar_show) {
        uri += "&metar=1";
    }
    if (madis_show) {
        uri += "&madis=1";
    }
    window.history.pushState({}, "", uri);
}

function handleDatePickerChange() {
    // Simply submit the form when date changes - PHP will handle the rest
    document.getElementById("theform").submit();
}

function handlePrevButtonClick() {
    const prevButton = document.getElementById("prevbutton");
    const targetDate = prevButton.dataset.date;
    if (targetDate) {
        navigateToDate(targetDate);
    }
}

function handleNextButtonClick() {
    const nextButton = document.getElementById("nextbutton");
    const targetDate = nextButton.dataset.date;
    if (targetDate && !nextButton.disabled) {
        navigateToDate(targetDate);
    }
}

function navigateToDate(dateStr) {
    // Build URL with current state preserved
    const sortDirElement = document.querySelector('select[name="sortdir"]');
    const windUnitsElement = document.querySelector('select[name="windunits"]');
    const sortDir = sortDirElement ? sortDirElement.value : "asc";
    const windUnits = windUnitsElement ? windUnitsElement.value : "mph";
    let url = `${window.location.origin}${window.location.pathname}?`+
        `station=${station}&network=${network}&date=${dateStr}&sortdir=${sortDir}&windunits=${windUnits}`;
    if (metar_show) {
        url += "&metar=1";
    }
    if (madis_show) {
        url += "&madis=1";
    }
    // Navigate to the new URL
    window.location.href = url;
}
function showMETAR() {
    document.querySelectorAll(".metar").forEach(element => {
        element.style.display = "table-row";
    });
    if (madis_show) {
        document.querySelectorAll(".hfmetar").forEach(element => {
            element.style.display = "table-row";
        });
    }
    document.getElementById("metar_toggle").innerHTML = "<i class=\"bi bi-dash-lg\" aria-hidden=\"true\"></i> Hide METARs";
}

function toggleMETAR() {
    if (metar_show) {
        // Hide both METARs and HFMETARs
        document.querySelectorAll(".metar").forEach(element => {
            element.style.display = "none";
        });
        document.querySelectorAll(".hfmetar").forEach(element => {
            element.style.display = "none";
        });
    document.getElementById("metar_toggle").innerHTML = "<i class=\"bi bi-plus-lg\" aria-hidden=\"true\"></i> Show METARs";
        document.getElementById("hmetar").value = "0";
    } else {
        // show
        showMETAR();
        document.getElementById("hmetar").value = "1";
    }
    metar_show = !metar_show;
    updateURI();
}

function showMADIS() {
    document.querySelectorAll("tr[data-madis='1']").forEach(element => {
        element.style.display = "table-row";
    });
    if (metar_show) {
        document.querySelectorAll(".hfmetar").forEach(element => {
            element.style.display = "table-row";
        });
    }
    document.getElementById("madis_toggle").innerHTML = "<i class=\"bi bi-dash-lg\" aria-hidden=\"true\"></i> Hide High Frequency MADIS";
}

function toggleMADIS() {
    if (madis_show) {
        // Hide MADIS
        document.querySelectorAll("tr[data-madis='1']").forEach(element => {
            element.style.display = "none";
        });
        document.querySelectorAll(".hfmetar").forEach(element => {
            element.style.display = "none";
        });
    document.getElementById("madis_toggle").innerHTML = "<i class=\"bi bi-plus-lg\" aria-hidden=\"true\"></i> Show High Frequency MADIS";
        document.getElementById("hmadis").value = "0";
    } else {
        // Show
        showMADIS();
        document.getElementById("hmadis").value = "1";
    }
    madis_show = !madis_show;
    updateURI();
}

document.addEventListener('DOMContentLoaded', () => {
    // Get form values
    const hiddenStation = document.querySelector('input[name="station"]');
    const hiddenNetwork = document.querySelector('input[name="network"]');
    
    station = hiddenStation.value;
    network = hiddenNetwork.value;
    metar_show = document.getElementById("hmetar").value === "1";
    madis_show = document.getElementById("hmadis").value === "1";
    
    // Set up event listeners
    const metar_toggle = document.getElementById("metar_toggle");
    if (metar_toggle) {
        metar_toggle.addEventListener('click', toggleMETAR);
    }
    const madis_toggle = document.getElementById("madis_toggle");
    if (madis_toggle) {
        madis_toggle.addEventListener('click', toggleMADIS);
    }
    requireElement("date_picker").addEventListener('change', handleDatePickerChange);
    requireElement("prevbutton").addEventListener('click', handlePrevButtonClick);
    requireElement("nextbutton").addEventListener('click', handleNextButtonClick);
    
    // Initial state for METAR/MADIS display
    if (metar_show) {
        showMETAR();
    }
    if (madis_show) {
        showMADIS();
    }
});
