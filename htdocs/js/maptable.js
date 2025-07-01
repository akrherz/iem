/* global ol */
/* A combination Openlayers Map + DataTable

Example:

<div
    class="iem-maptable row"
    data-label-field="sname"
    data-geojson-src="/geojson/networks.geojson?network=IA_ASOS">
</div>

*/

function get_style(color, text) {
    return new ol.style.Style({
        fill: new ol.style.Fill({
            color: 'rgba(255, 255, 255, 0.6)'
        }),
        text: new ol.style.Text({
            font: '14px Calibri,sans-serif',
            text,
            fill: new ol.style.Fill({
                color,
                width: 1
            }),
            stroke: new ol.style.Stroke({
                color: '#FFF',
                width: 3
            })
        })
    });
}


function getLabelForFeature(inst, feat) {
    let label = "TBD";
    if (inst.label_field === "id") {
        label = feat.getId();
    } else if (inst.label_field) {
        label = feat.get(inst.label_field).toString();
    }
    return label;
}


function highlightFeature(inst, feat) {
    if (inst.selectedFeature) {
        inst.selectedFeature.setStyle(null);
    }
    inst.selectedFeature = feat;
    feat.setStyle(get_style("#F00", getLabelForFeature(inst, feat)));
}


function init_map(idx, inst) {
    inst.selectedFeature = null;
    inst.vectorLayer = new ol.layer.Vector({
        title: 'Data',
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        }),
        style: (feature) => [get_style("#000", getLabelForFeature(inst, feature))]
    });
    fetch(inst.geojson_src)
        .then(resp => resp.json())
        .then(data => {
            if (data.meta) {
                inst.label_field = data.meta.propdefault;
                inst.proporder = data.meta.proporder;
            }
            inst.vectorLayer.getSource().addFeatures(
                (new ol.format.GeoJSON({ featureProjection: 'EPSG:3857' })).readFeatures(data)
            );
            buildTabulatorTable(idx, inst, data);
        });
    inst.map = new ol.Map({
        target: inst.mapdiv,
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                source: new ol.source.OSM()
            }),
            inst.vectorLayer
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: [-10575351, 5160979],
            zoom: 3
        })
    });
    inst.map.on('click', (evt) => {
        const feature = inst.map.forEachFeatureAtPixel(evt.pixel,
            (feature2) => feature2);
        if (!feature) {
            return;
        }
        highlightFeature(inst, feature);
        const id = feature.getId();
        inst.table.deselectRow();
        const rows = inst.table.getRows();
        for (const row of rows) {
            if (row.getData().id === id) {
                row.select();
                break;
            }
        }
    });

    inst.vectorLayer.getSource().on('change', () => {
        if (inst.vectorLayer.getSource().getState() === 'ready' && inst.zoomReset === false) {
            inst.map.getView().fit(
                inst.vectorLayer.getSource().getExtent(),
                {
                    size: inst.map.getSize(),
                    padding: [50, 50, 50, 50]
                }
            );
            inst.zoomReset = true;
        }
    });
}

function buildTabulatorTable(idx, inst, data) {
    // Build columns and data array for Tabulator
    const columns = [{ title: 'ID', field: 'id', headerSort: true }];
    inst.select.innerHTML = '';
    const idOption = document.createElement('option');
    idOption.value = 'id';
    idOption.textContent = 'ID';
    inst.select.appendChild(idOption);
    let proporder = inst.proporder || [];
    if (proporder.length === 0 && data.features && data.features.length > 0) {
        proporder = Object.keys(data.features[0].properties).filter(k => k !== 'id' && k !== 'geometry');
    }
    proporder.forEach((val) => {
        columns.push({ title: val, field: val, headerSort: true });
        const opt = document.createElement('option');
        opt.value = val;
        opt.textContent = val;
        inst.select.appendChild(opt);
    });
    const tableData = data.features.map(f => ({ ...f.properties, id: f.id }));
    const table = new window.Tabulator(`#maptable-table${idx}`, {
        data: tableData,
        columns,
        layout: "fitDataStretch",
        height: 400,
        selectable: 1,
        pagination: false,
        rowClick(e, row) {
            const id = row.getData().id;
            const feat = inst.vectorLayer.getSource().getFeatureById(id);
            if (feat) {
                highlightFeature(inst, feat);
            }
        },
        rowSelected(row) {
            const id = row.getData().id;
            const feat = inst.vectorLayer.getSource().getFeatureById(id);
            if (feat) {
                highlightFeature(inst, feat);
            }
        }
    });
    inst.table = table;
    // When select changes, update label field and restyle
    inst.select.addEventListener('change', function() {
        inst.label_field = this.value;
        inst.vectorLayer.setStyle(inst.vectorLayer.getStyle());
        if (inst.selectedFeature) {
            highlightFeature(inst, inst.selectedFeature);
        }
    });
}

function init(idx, div) {
    // Setup the given div for usage
    // Add left and right hand side divs
    const inst = {};
    inst.proporder = null;
    inst.zoomReset = false;
    inst.geojson_src = div.getAttribute('data-geojson-src');
    inst.label_field = div.getAttribute('data-label-field');
    const leftcol = document.createElement('div');
    leftcol.className = 'col-md-6';
    inst.mapdiv = document.createElement('div');
    inst.mapdiv.style = "height: 400px";
    leftcol.append(inst.mapdiv);
    const pp = document.createElement('p');
    const tt = document.createTextNode("Select variable for labels:");
    pp.appendChild(tt);
    inst.select = document.createElement('select');
    pp.appendChild(inst.select);
    // Handled in buildTabulatorTable
    leftcol.appendChild(pp);
    div.append(leftcol);
    const tablediv = document.createElement('div');
    tablediv.className = 'col-md-6';
    const tableElement = document.createElement('table');
    tableElement.id = `maptable-table${idx}`;
    tablediv.appendChild(tableElement);
    div.append(tablediv);

    init_map(idx, inst);
    return inst;
}

window.addEventListener('DOMContentLoaded', () => {
    const maptables = document.querySelectorAll('div.iem-maptable');
    maptables.forEach((div, idx) => {
        init(idx, div);
    });
});