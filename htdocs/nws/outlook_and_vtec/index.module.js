
const parseRows = () => {
    const node = document.getElementById("tableRows");
    if (!node) {
        return [];
    }
    try {
        const parsed = JSON.parse(node.textContent || "[]");
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
};

const containsSearchTerm = (row, term) => {
    if (!term) {
        return true;
    }
    const haystack = [
        row.date,
        row.utc_issue,
        row.utc_expire,
        row.outlook,
        row.events_text,
    ]
        .join(" ")
        .toLowerCase();
    return haystack.includes(term.toLowerCase());
};

document.addEventListener("DOMContentLoaded", () => {
    const tableElement = document.getElementById("eventsTable");
    const summaryElement = document.getElementById("tableSummary");
    const searchElement = document.getElementById("tableSearch");
    const withEventsElement = document.getElementById("onlyWithEvents");
    const tabulatorClass = window.Tabulator;
    if (!tableElement || typeof tabulatorClass === "undefined") {
        return;
    }

    const rows = parseRows();
    let searchTerm = "";
    let isTableBuilt = false;

    const table = new tabulatorClass(tableElement, {
        data: rows,
        layout: "fitColumns",
        responsiveLayout: "collapse",
        placeholder: "No outlook records match the current filters.",
        initialSort: [{ column: "date", dir: "desc" }],
        columns: [
            { title: "Date", field: "date", width: 120, headerSort: true },
            { title: "UTC Issue", field: "utc_issue", width: 140 },
            { title: "UTC Expire", field: "utc_expire", width: 140 },
            {
                title: "Outlook",
                field: "outlook",
                minWidth: 220,
                formatter: "plaintext",
            },
            {
                title: "Event Count",
                field: "event_count",
                hozAlign: "center",
                width: 120,
            },
            {
                title: "Coincident VTEC Events",
                field: "events_html",
                minWidth: 360,
                formatter: "html",
            },
        ],
    });

    const applyFilters = () => {
        if (!isTableBuilt) {
            return;
        }
        const onlyWithEvents = withEventsElement?.checked ?? true;
        table.setFilter((data) => {
            const passEvents = !onlyWithEvents || Number(data.event_count) > 0;
            const passSearch = containsSearchTerm(data, searchTerm);
            return passEvents && passSearch;
        });
    };

    const updateSummary = () => {
        if (!isTableBuilt) {
            return;
        }
        const visibleRows = table.getDataCount("active");
        const totalRows = rows.length;
        const rowsWithEvents = rows.filter((row) => Number(row.event_count) > 0).length;
        if (summaryElement) {
            summaryElement.textContent =
                `${visibleRows} shown of ${totalRows} total outlooks (${rowsWithEvents} with events).`;
        }
    };

    if (searchElement) {
        searchElement.addEventListener("input", () => {
            searchTerm = searchElement.value.trim();
            applyFilters();
        });
    }
    if (withEventsElement) {
        withEventsElement.addEventListener("change", applyFilters);
    }

    table.on("dataFiltered", updateSummary);
    table.on("tableBuilt", () => {
        isTableBuilt = true;
        applyFilters();
        updateSummary();
    });
});
