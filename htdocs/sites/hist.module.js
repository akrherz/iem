/* global Tabulator */

function makeElement(tag, className = '', text = '') {
    const element = document.createElement(tag);
    if (className) {
        element.className = className;
    }
    if (text !== '') {
        element.textContent = text;
    }
    return element;
}

function addLine(container, label, value) {
    const line = makeElement('div');
    line.append(document.createTextNode(`${label}${value}`));
    container.append(line);
}

function displayValue(value, missing = '') {
    return value === null || value === undefined ? missing : String(value);
}

function fixedValue(value, digits) {
    return value === null || value === undefined
        ? 'M'
        : Number(value).toFixed(digits);
}

function precipValue(value, digits = 2) {
    if (value === null || value === undefined || value === '') {
        return 'M';
    }
    if (value === 'T') {
        return value;
    }
    const amount = Number(value);
    if (amount > 0 && amount < 0.005) {
        return 'T';
    }
    return amount.toFixed(digits);
}

function snowValue(value) {
    return precipValue(value, 1);
}

function directionText(direction) {
    if (direction === null || direction === undefined) {
        return 'N';
    }
    const value = Number.parseInt(direction, 10);
    const directions = [
        ['N', 350, 361],
        ['N', 0, 13],
        ['NNE', 13, 35],
        ['NE', 35, 57],
        ['ENE', 57, 80],
        ['E', 80, 102],
        ['ESE', 102, 127],
        ['SE', 127, 143],
        ['SSE', 143, 166],
        ['S', 166, 190],
        ['SSW', 190, 215],
        ['SW', 215, 237],
        ['WSW', 237, 260],
        ['W', 260, 281],
        ['WNW', 281, 304],
        ['NW', 304, 324],
        ['NNW', 324, 350],
    ];
    const match = directions.find(([, lower, upper]) => (
        value >= lower && value < upper
    ));
    return match ? match[0] : '';
}

function localTime(value) {
    if (!value) {
        return '';
    }
    const match = String(value).match(/[T ](\d{1,2}):(\d{2})/);
    if (!match) {
        return '';
    }
    const hour = Number(match[1]);
    const suffix = hour >= 12 ? 'PM' : 'AM';
    return `${hour % 12 || 12}:${match[2]} ${suffix}`;
}

function addTemperatureLines(row, cell) {
    if (row.max_tmpf !== null && row.max_tmpf !== undefined) {
        addLine(cell, 'High: ', `${row.max_tmpf}${row.tmpf_est ? '(E)' : ''}`);
    }
    if (row.min_tmpf !== null && row.min_tmpf !== undefined) {
        addLine(cell, 'Low: ', `${row.min_tmpf}${row.tmpf_est ? '(E)' : ''}`);
    }
}

function addPrecipitationLine(row, cell) {
    const precipText = row.precip > 0 && row.precip < 0.01
        ? 'Trace '
        : row.precip === null || row.precip === undefined
            ? 'M'
            : fixedValue(row.precip, 2);
    addLine(cell, 'Precip: ', `${precipText}${row.precip_est ? '(E)' : ''}`);
}

function addStageAndSnowLines(row, cell) {
    if (row.max_rstage !== null && row.max_rstage !== undefined
        && row.max_rstage >= 0) {
        addLine(cell, 'Max Stage[ft]: ', fixedValue(row.max_rstage, 2));
    }
    if (row.snow !== null && row.snow !== undefined && row.snow >= 0) {
        addLine(cell, 'Snow: ', snowValue(row.snow));
    }
    if (row.snowd !== null && row.snowd !== undefined && row.snowd >= 0) {
        addLine(cell, 'Snow Depth: ', snowValue(row.snowd));
    }
}

function addWindLines(row, cell) {
    if (row.avg_sknt !== null && row.avg_sknt !== undefined) {
        addLine(
            cell,
            'Avg Wind: ',
            `${directionText(row.vector_avg_drct)} @ ${(row.avg_sknt * 1.15).toFixed(1)}`,
        );
    }
    if (row.max_gust !== null && row.max_gust !== undefined
        && row.max_gust_localts) {
        const gust = Math.round(row.max_gust * 1.15);
        const time = localTime(row.max_gust_localts);
        const direction = row.max_drct === null || row.max_drct === undefined
            ? ''
            : directionText(row.max_drct);
        addLine(
            cell,
            'Gust: ',
            `${direction ? `${direction} @ ` : ''}${gust} (${time})`,
        );
    }
}

function addHumidityAndFeelLines(row, cell) {
    if (row.min_rh !== null && row.min_rh !== undefined) {
        addLine(
            cell,
            'RH% Min/Max: ',
            `${Number(row.min_rh).toFixed(0)}-${Number(row.max_rh).toFixed(0)}`,
        );
    }
    if (row.min_feel !== null && row.min_feel !== undefined) {
        addLine(
            cell,
            'Feel Min/Max: ',
            `${Number(row.min_feel).toFixed(0)} to ${Number(row.max_feel).toFixed(0)}`,
        );
    }
}

function calendarDayText(row, cell) {
    addTemperatureLines(row, cell);
    addPrecipitationLine(row, cell);
    addStageAndSnowLines(row, cell);
    addWindLines(row, cell);
    addHumidityAndFeelLines(row, cell);
}

function pageUrl(params) {
    return `/sites/hist.phtml?${new URLSearchParams(params).toString()}`;
}

function makeApiUrls(config) {
    const params = new URLSearchParams({ network: config.network });
    if (config.mode === 'monthly') {
        params.set('station', config.station);
        params.set('month', config.month);
        params.set('year', config.year);
    } else {
        params.set(
            'date',
            `${config.year}-${String(config.month).padStart(2, '0')}-${String(config.day).padStart(2, '0')}`,
        );
    }
    return {
        json: `/api/1/daily.json?${params.toString()}`,
        csv: `/api/1/daily.txt?${params.toString()}`,
    };
}

function addApiDescription(container, urls) {
    const paragraph = makeElement('p');
    paragraph.append(document.createTextNode('The data presented here is provided by '));
    const apiLink = makeElement('a', '', 'IEM API');
    apiLink.href = '/api/';
    paragraph.append(apiLink, document.createTextNode(' webservice: '));
    const jsonLink = makeElement('a', '', 'daily.json');
    jsonLink.href = urls.json;
    paragraph.append(jsonLink, document.createTextNode('. A simple '));
    const csvLink = makeElement('a', '', 'CSV option');
    csvLink.href = urls.csv;
    paragraph.append(csvLink, document.createTextNode(' exists as well.'));
    container.append(paragraph);
}

function dateLabel(year, month) {
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        year: 'numeric',
        timeZone: 'UTC',
    }).format(new Date(Date.UTC(year, month - 1, 1)));
}

function renderCalendar(container, rows, config) {
    const year = Number(config.year);
    const month = Number(config.month);
    const firstDow = new Date(Date.UTC(year, month - 1, 1)).getUTCDay();
    const daysInMonth = new Date(Date.UTC(year, month, 0)).getUTCDate();
    const numberOfWeeks = Math.ceil((firstDow + daysInMonth) / 7);
    const observations = new Map(
        rows.map((row) => [String(row.date).slice(0, 10), row]),
    );
    const table = makeElement('table', 'table table-bordered');
    const head = makeElement('thead');
    const navigationRow = makeElement('tr');
    const previous = new Date(Date.UTC(year, month - 2, 1));
    const next = new Date(Date.UTC(year, month, 1));
    const previousParams = {
        network: config.network,
        station: config.station,
        year: previous.getUTCFullYear(),
        month: previous.getUTCMonth() + 1,
    };
    const nextParams = {
        network: config.network,
        station: config.station,
        year: next.getUTCFullYear(),
        month: next.getUTCMonth() + 1,
    };
    const previousCell = makeElement('td');
    const previousLink = makeElement('a', '', dateLabel(
        previous.getUTCFullYear(),
        previous.getUTCMonth() + 1,
    ));
    previousLink.href = pageUrl(previousParams);
    previousCell.append(previousLink);
    const titleCell = makeElement('th', '', dateLabel(year, month));
    titleCell.colSpan = 5;
    const nextCell = makeElement('td');
    const nextLink = makeElement('a', '', dateLabel(
        next.getUTCFullYear(),
        next.getUTCMonth() + 1,
    ));
    nextLink.href = pageUrl(nextParams);
    nextCell.append(nextLink);
    navigationRow.append(previousCell, titleCell, nextCell);
    head.append(navigationRow);

    const headings = makeElement('tr');
    ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        .forEach((day) => headings.append(makeElement('th', '', day)));
    head.append(headings);
    table.append(head);

    const body = makeElement('tbody');
    for (let week = 0; week < numberOfWeeks; week += 1) {
        const row = makeElement('tr');
        for (let day = 0; day < 7; day += 1) {
            const dayNumber = week * 7 + day - firstDow + 1;
            const inMonth = dayNumber >= 1 && dayNumber <= daysInMonth;
            const date = new Date(Date.UTC(year, month - 1, dayNumber));
            const cell = makeElement('td');
            cell.style.verticalAlign = 'top';
            if (!inMonth) {
                cell.style.backgroundColor = '#EEEEEE';
            }
            const dayLabel = String(date.getUTCDate()).padStart(2, '0');
            const dayHeader = makeElement('strong');
            if (inMonth) {
                const params = {
                    network: config.network,
                    station: config.station,
                    mode: 'daily',
                    year,
                    month,
                    day: dayNumber,
                };
                const link = makeElement('a', '', dayLabel);
                link.href = pageUrl(params);
                dayHeader.append(link);
                const observation = observations.get(
                    `${year}-${String(month).padStart(2, '0')}-${dayLabel}`,
                );
                if (observation?.temp_hour) {
                    dayHeader.append(document.createTextNode(` (@${observation.temp_hour})`));
                }
                if (observation) {
                    calendarDayText(observation, cell);
                }
            } else {
                dayHeader.textContent = dayLabel;
            }
            cell.prepend(dayHeader);
            row.append(cell);
        }
        body.append(row);
    }
    table.append(body);
    container.append(table);
}

function addMonthlyCharts(container, config) {
    const chart17 = `/plotting/auto/plot/17/month:${config.month}::year:${config.year}::station:${encodeURIComponent(config.station)}::network:${encodeURIComponent(config.network)}`;
    const charts = [
        {
            title: 'Daily High/Low Plot',
            url: `${chart17}.png`,
            description: 'This chart of the monthly temperature data. The bars are the observations and the dots are climatology.',
        },
        {
            title: 'Daily Rainfall',
            url: `${chart17}::p:precip.png`,
            description: 'This chart is of daily precipitation for the month. The red line would be an average month while the blue line and bars are observations.',
        },
        {
            title: 'Daily Average Wind Speeds',
            url: `/plotting/auto/plot/71/network:${encodeURIComponent(config.network)}::zstation:${encodeURIComponent(config.station)}::year:${config.year}::month:${config.month}::units:MPH::dpi:100.png`,
            description: 'This chart is of the daily average wind speeds.',
        },
    ];
    charts.forEach((chart) => {
        container.append(makeElement('h3', '', chart.title));
        const image = makeElement('img', 'img-fluid');
        image.src = chart.url;
        image.alt = chart.title;
        container.append(image);
        const description = makeElement('p');
        description.append(
            makeElement('strong', '', 'Description: '),
            document.createTextNode(chart.description),
        );
        container.append(description);
    });
}

function tableRows(rows) {
    return rows.map((row) => {
        const gustAvailable = row.max_gust !== null && row.max_gust !== undefined
            && row.max_gust_localts;
        const gustDirection = row.max_drct === null || row.max_drct === undefined
            ? ''
            : `${directionText(row.max_drct)} @ `;
        const gust = gustAvailable
            ? `${gustDirection}${Math.round(row.max_gust * 1.15)}`
            : '';
        const label = `${displayValue(row.name)}${row.temp_hour ? ` (@ ${row.temp_hour})` : ''}`;
        const estimatedTemp = row.tmpf_est ? ' (E)' : '';
        return {
            id: displayValue(row.station),
            location: label,
            high: `${displayValue(row.max_tmpf, 'M')}${estimatedTemp}`,
            low: `${displayValue(row.min_tmpf, 'M')}${estimatedTemp}`,
            min_feels: displayValue(row.min_feel),
            max_feels: displayValue(row.max_feel),
            min_dew: displayValue(row.min_dwpf),
            max_dew: displayValue(row.max_dwpf),
            rainfall: `${precipValue(row.precip)}${row.precip_est ? ' (E)' : ''}`,
            peak_gust: gust,
            gust_time: gustAvailable ? localTime(row.max_gust_localts) : '',
            snowfall: snowValue(row.snow),
            snow_depth: snowValue(row.snowd),
        };
    });
}

function renderDailyTable(container, rows, config) {
    const table = makeElement('div');
    table.id = 'thetable';
    container.append(table);
    new Tabulator(table, {
        data: tableRows(rows),
        layout: 'fitColumns',
        responsiveLayout: 'collapse',
        columns: [
            { title: 'ID:', field: 'id' },
            {
                title: 'Location:',
                field: 'location',
                formatter: (cell) => {
                    const row = cell.getRow().getData();
                    const link = makeElement('a', '', row.location);
                    link.href = pageUrl({
                        network: config.network,
                        year: config.year,
                        month: config.month,
                        mode: 'monthly',
                        station: row.id,
                    });
                    return link;
                },
            },
            { title: 'High:', field: 'high' },
            { title: 'Low:', field: 'low' },
            { title: 'Min Feels Like[F]:', field: 'min_feels' },
            { title: 'Max Feels Like [F]:', field: 'max_feels' },
            { title: 'Min Dew Point [F]:', field: 'min_dew' },
            { title: 'Max Dew Point [F]:', field: 'max_dew' },
            { title: 'Rainfall:', field: 'rainfall' },
            { title: 'Peak Gust:', field: 'peak_gust' },
            { title: 'Time of Gust:', field: 'gust_time' },
            { title: 'Snowfall:', field: 'snowfall' },
            { title: 'Snow Depth:', field: 'snow_depth' },
        ],
    });
}

async function loadData(config, mount) {
    const urls = makeApiUrls(config);
    const response = await fetch(urls.json);
    if (!response.ok) {
        throw new Error(`The API request failed with status ${response.status}.`);
    }
    const result = await response.json();
    if (!Array.isArray(result.data)) {
        throw new Error('The API response did not contain a data array.');
    }

    const content = makeElement('div');
    if (config.mode === 'monthly') {
        renderCalendar(content, result.data, config);
        addMonthlyCharts(content, config);
    } else {
        renderDailyTable(content, result.data, config);
    }
    addApiDescription(content, urls);
    mount.replaceChildren(content);
}

document.addEventListener('DOMContentLoaded', () => {
    const mount = document.getElementById('hist-app');
    if (!mount) {
        return;
    }
    const config = mount.dataset;
    loadData(config, mount).catch((error) => {
        const message = makeElement(
            'p',
            'alert alert-danger',
            `Unable to load daily data: ${error.message}`,
        );
        mount.replaceChildren(message);
    });
});
