
// Migration to ES Module, Tabulator, and Bootstrap 5 (rules: ES module, no jQuery, Tabulator, Bootstrap5)
import { TabulatorFull as Tabulator } from "https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs";

// Fetch the data from the backend JSON endpoint
fetch("/json/watches.py?is_pds=1")
  .then((resp) => resp.json())
  .then((json) => {
    const tableData = json.events.map(val => ({
      year: val.year,
      watch: `<a target="_blank" href="https://www.spc.noaa.gov/products/watch/${val.year}/ww${val.num.toString().padStart(4, '0')}.html">${val.type} ${val.num}</a>`,
      states: val.states,
      issue: val.issue,
      expire: val.expire,
      tornadoes_1m_strong: val.tornadoes_1m_strong,
      hail_1m_2inch: val.hail_1m_2inch,
      max_hail_size: val.max_hail_size,
      max_wind_gust_knots: val.max_wind_gust_knots
    }));

    const columns = [
      { title: "Year", field: "year", headerFilter: true, width: 80 },
      { title: "Watch Num", field: "watch", formatter: "html", width: 130 },
      { title: "State(s)", field: "states", headerFilter: true },
      { title: "Issued", field: "issue", sorter: "datetime", width: 160 },
      { title: "Expired", field: "expire", sorter: "datetime", width: 160 },
      { title: "Prob EF2+ Tor", field: "tornadoes_1m_strong", hozAlign: "center", width: 120 },
      { title: "Prob Hail 2+in", field: "hail_1m_2inch", hozAlign: "center", width: 120 },
      { title: "Max Hail Size", field: "max_hail_size", hozAlign: "center", width: 120 },
      { title: "Max Wind Gust kts", field: "max_wind_gust_knots", hozAlign: "center", width: 140 },
    ];

    new Tabulator("#pds-table", {
      data: tableData,
      columns,
      layout: "fitDataStretch",
      responsiveLayout: true,
      height: "600px",
      movableColumns: true,
      pagination: true,
      paginationSize: 25,
      paginationSizeSelector: [25, 50, 100, true],
      placeholder: "No PDS Watches found.",
      headerSortTristate: true,
      columnDefaults: { resizable: true },
      // Bootstrap 5 styling
      rowFormatter: row => row.getElement().classList.add('align-middle'),
      // Export options
      downloadConfig: { columnHeaders: true, columnGroups: false, rowGroups: false, columnCalcs: false },
      downloadRowRange: "all",
      downloadReady: (fileContents, blob) => blob,
      // Add download buttons
      renderComplete() {
        if (!document.getElementById('tab-download-btns')) {
          const btns = document.createElement('div');
          btns.id = 'tab-download-btns';
          btns.className = 'mb-3';
          btns.innerHTML =
            '<button class="btn btn-outline-secondary btn-sm me-2" id="tab-csv">Download CSV</button>' +
            '<button class="btn btn-outline-secondary btn-sm me-2" id="tab-xlsx">Download XLSX</button>' +
            '<button class="btn btn-outline-secondary btn-sm" id="tab-json">Download JSON</button>';
          const parent = document.querySelector('#pds-table').parentElement;
          parent.insertBefore(btns, document.querySelector('#pds-table'));
          document.getElementById('tab-csv').onclick = () => this.download('csv', 'pds_watches.csv');
          document.getElementById('tab-xlsx').onclick = () => this.download('xlsx', 'pds_watches.xlsx');
          document.getElementById('tab-json').onclick = () => this.download('json', 'pds_watches.json');
        }
      }
    });
  });
