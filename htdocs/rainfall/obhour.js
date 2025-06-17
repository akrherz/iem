/* global Ext, Date */

let defaultnetwork = null;
let gpanel = null;

const networks = [
    ['IA_ASOS', 'Iowa ASOS/AWOS'],
    ['AL_ASOS', 'Alabama ASOS/AWOS'],
    ['AK_ASOS', 'Alaska ASOS/AWOS'],
    ['AZ_ASOS', 'Arizona ASOS/AWOS'],
    ['AR_ASOS', 'Arkansas ASOS/AWOS'],
    ['CA_ASOS', 'California ASOS/AWOS'],
    ['CO_ASOS', 'Colorado ASOS/AWOS'],
    ['CT_ASOS', 'Connect. ASOS/AWOS'],
    ['DE_ASOS', 'Delaware ASOS/AWOS'],
    ['FL_ASOS', 'Florida ASOS/AWOS'],
    ['GA_ASOS', 'Georgia ASOS/AWOS'],
    ['HI_ASOS', 'Hawaii ASOS/AWOS'],
    ['ID_ASOS', 'Idaho ASOS/AWOS'],
    ['IL_ASOS', 'Illinois ASOS/AWOS'],
    ['IN_ASOS', 'Indiana ASOS/AWOS'],
    ['KS_ASOS', 'Kansas ASOS/AWOS'],
    ['KY_ASOS', 'Kentucky ASOS/AWOS'],
    ['LA_ASOS', 'Louisana ASOS/AWOS'],
    ['MA_ASOS', 'Mass. ASOS/AWOS'],
    ['MD_ASOS', 'Maryland ASOS/AWOS'],
    ['ME_ASOS', 'Maine ASOS/AWOS'],
    ['MI_ASOS', 'Michigan ASOS/AWOS'],
    ['MN_ASOS', 'Minnesota ASOS/AWOS'],
    ['MO_ASOS', 'Missouri ASOS/AWOS'],
    ['MS_ASOS', 'Mississippi ASOS/AWOS'],
    ['MT_ASOS', 'Montana ASOS/AWOS'],
    ['NC_ASOS', 'North Carolina ASOS/AWOS'],
    ['NE_ASOS', 'Nebraska ASOS/AWOS'],
    ['NV_ASOS', 'Nevada ASOS/AWOS'],
    ['NH_ASOS', 'New Hampshire ASOS/AWOS'],
    ['NJ_ASOS', 'New Jersey ASOS/AWOS'],
    ['NM_ASOS', 'New Mexico ASOS/AWOS'],
    ['NY_ASOS', 'New York ASOS/AWOS'],
    ['ND_ASOS', 'North Dakota ASOS/AWOS'],
    ['OH_ASOS', 'Ohio ASOS/AWOS'],
    ['OK_ASOS', 'Oklahoma ASOS/AWOS'],
    ['OR_ASOS', 'Oregon ASOS/AWOS'],
    ['PA_ASOS', 'Pennsylvania ASOS/AWOS'],
    ['PR_ASOS', 'Puerto Rico ASOS/AWOS'],
    ['RI_ASOS', 'Rhode Island ASOS/AWOS'],
    ['SC_ASOS', 'South Carolina ASOS/AWOS'],
    ['SD_ASOS', 'South Dakota ASOS/AWOS'],
    ['TN_ASOS', 'Tennessee ASOS/AWOS'],
    ['TX_ASOS', 'Texas ASOS/AWOS'],
    ['UT_ASOS', 'Utah ASOS/AWOS'],
    ['VA_ASOS', 'Virginia ASOS/AWOS'],
    ['VT_ASOS', 'Vermont ASOS/AWOS'],
    ['VI_ASOS', 'Virgin Islands ASOS/AWOS'],
    ['WA_ASOS', 'Washington ASOS/AWOS'],
    ['WI_ASOS', 'Wisconsin ASOS/AWOS'],
    ['WV_ASOS', 'West Virginia ASOS/AWOS'],
    ['WY_ASOS', 'Wyoming ASOS/AWOS']
];

function updateURI(network) {
    // set the URI
    const url = new URL(window.location);
    url.searchParams.set('network', network);
    window.history.pushState({}, '', url);
}
function rpv(val) {
    if ((val > 0) && (val < 0.009)) return "T";
    return val;
}

Ext.onReady(() => {

    defaultnetwork = new URL(window.location).searchParams.get('network') || 'IA_ASOS';

    const network_selector = new Ext.form.ComboBox({
        hiddenName: 'network',
        store: new Ext.data.SimpleStore({
            fields: ['abbr', 'name'],
            data: networks
        }),
        valueField: 'abbr',
        displayField: 'name',
        hideLabel: true,
        typeAhead: true,
        mode: 'local',
        triggerAction: 'all',
        emptyText: 'Select a Network...',
        selectOnFocus: true,
        lazyRender: true,
        value: defaultnetwork,
        width: 190
    });


    const dateselector = new Ext.form.DateField({
        id: "df",
        width: 150,
        hideLabel: true,
        minValue: new Date('2008/01/01'),
        maxValue: new Date(),
        value: new Date()
    });

    const timeselector = new Ext.form.TimeField({
        hideLabel: true,
        increment: 60,
        value: new Date(),
        format: 'h A',
        id: "tm"
    });

    const realtime = new Ext.form.Checkbox({
        id: "realtime",
        boxLabel: "Auto Refresh",
        hideLabel: true
    });

    const task = {
        run() {
            if (!realtime.checked) return;
            const localDate = new Date();
            dateselector.setValue(localDate);
            timeselector.setValue(localDate);
            const gmtDate = localDate.add(Date.SECOND, 0 - localDate.format('Z'));
            const sff = Ext.getCmp('selectform').getForm();
            const network = sff.findField('network').getValue();
            Ext.getCmp('precipgrid').setTitle(`Precip Accumulation valid at ${localDate.format('d M Y h A')}`).getStore().load({
                params: `network=${network}&ts=${gmtDate.format('YmdHi')}`
            });
            Ext.getCmp('statusField').setText(`Grid Loaded at ${new Date()}`);
            updateHeaders(localDate);

        },
        interval: 1200000
    };
    Ext.TaskMgr.start(task);


    const selectform = new Ext.form.FormPanel({
        frame: true,
        id: 'selectform',
        title: 'Data Chooser',
        labelWidth: 0,
        buttons: [{
            text: 'Load Data',
            handler() {
                const sff = Ext.getCmp('selectform').getForm();
                const network = sff.findField('network').getValue();
                updateURI(network);
                let localDate = sff.findField('df').getValue();
                const tm = sff.findField('tm').getValue();
                const dt = new Date.parseDate(tm, 'h A');
                localDate = localDate.add(Date.HOUR, dt.format('H'));
                const gmtDate = localDate.add(Date.SECOND, 0 - localDate.format('Z'));
                Ext.getCmp('precipgrid')
                    .setTitle(`Precip Accumulation valid at ${localDate.format('d M Y h A')}`)
                    .getStore()
                    .load({
                        params: `network=${network}&ts=${gmtDate.format('YmdHi')}`
                    });
                Ext.getCmp('statusField').setText(`Grid Loaded at ${new Date()}`);
                updateHeaders(localDate);
            } // End of handler
        }],
        items: [network_selector, dateselector, timeselector, realtime]
    });

    // http://www.sencha.com/forum/showthread.php?43298-HttpProxy-timeout-always-30-secs
    const conn = new Ext.data.Connection({
        timeout: 120000
        , url: 'obhour-json.php'
        , method: 'GET'
    });

    const pstore = new Ext.data.Store({
        root: 'precip',
        autoLoad: false,
        proxy: new Ext.data.HttpProxy(conn),
        reader: new Ext.data.JsonReader({
            root: 'precip',
            id: 'id'
        }, [
            { name: 'id' },
            { name: 'name' },
            { name: 'pmidnight' },
            { name: 'p1' },
            { name: 'p3' },
            { name: 'p6' },
            { name: 'p12' },
            { name: 'p24' },
            { name: 'p48' },
            { name: 'p72' },
            { name: 'p168' },
            { name: 'p720' },
            { name: 'p2160' },
            { name: 'p8760' }
        ])
    });

    function offset_render(hrs) {
        if (hrs < 24) { return `${hrs} Hour`; }
        return `${hrs / 24} Day`;
    };

    function updateHeaders(ts) {
        const cm = gpanel.getColumnModel();
        let col = null;
        let ts0 = null;
        for (let i = 2; i < cm.getColumnCount(); i++) {
            col = cm.getColumnById(cm.getColumnId(i));
            ts0 = ts.add(Date.SECOND, 0 - (col.toffset * 3600));
            if (col.toffset === 0) {
                ts0 = ts.add(Date.HOUR, 0 - (ts.format('H')));
                cm.setColumnHeader(i, `Midnight<br />${ts0.format('m/d hA')}<br />${ts.format('m/d hA')}`);
            } else {
                cm.setColumnHeader(i, `${offset_render(col.toffset)}<br />${ts0.format('m/d hA')}<br />${ts.format('m/d hA')}`);
            }
        }
    };

    gpanel = new Ext.grid.GridPanel({
        id: 'precipgrid',
        isLoaded: false,
        store: pstore,
        region: 'center',
        tbar: [new Ext.ux.StatusBar({
            defaultText: 'Please load data from the side',
            id: 'statusField'
        })
        ],
        loadMask: { msg: 'Loading Data... This may take a minute...' },
        viewConfig: { forceFit: false },
        cm: new Ext.grid.ColumnModel([
            { header: "ID", width: 40, sortable: true, dataIndex: 'id' },
            { header: "Name", id: "sitename", width: 150, sortable: true, dataIndex: 'name' },
            { header: "Midnight Central", toffset: 0, width: 80, sortable: true, dataIndex: 'pmidnight', renderer: rpv },
            { header: "1 Hour", toffset: 1, width: 80, sortable: true, dataIndex: 'p1', renderer: rpv },
            { header: "3 Hour", toffset: 3, width: 80, sortable: true, dataIndex: 'p3', renderer: rpv },
            { header: "6 Hour", toffset: 6, width: 80, sortable: true, dataIndex: 'p6', renderer: rpv },
            { header: "12 Hour", toffset: 12, width: 80, sortable: true, dataIndex: 'p12', renderer: rpv },
            { header: "24 Hour", toffset: 24, width: 80, sortable: true, dataIndex: 'p24', renderer: rpv },
            { header: "48 Hour", toffset: 48, width: 80, sortable: true, dataIndex: 'p48', renderer: rpv },
            { header: "72 Hour", toffset: 72, width: 80, sortable: true, dataIndex: 'p72', renderer: rpv },
            { header: "168 Hour", toffset: 168, width: 80, sortable: true, dataIndex: 'p168', renderer: rpv },
            { header: "720 Hour", toffset: 720, width: 80, sortable: true, dataIndex: 'p720', renderer: rpv },
            { header: "2160 Hour", toffset: 2160, width: 80, sortable: true, dataIndex: 'p2160', renderer: rpv },
            { header: "8760 Hour", toffset: 8760, width: 80, sortable: true, dataIndex: 'p8760', renderer: rpv }
        ]),
        stripeRows: true,
        title: 'Accumulated Precipitation by Interval',
        autoScroll: true
    });

    // Information panel for sidebar - Rule: Code comments explain functionality
    const tp = new Ext.Panel({
        html: `<div style="padding: 8px;">
            <h6>Quick Tips</h6>
            <ul style="font-size: 12px; margin: 5px 0;">
                <li>Select network and date/time to load data</li>
                <li>Enable "Auto Refresh" for real-time updates</li>
                <li>Times represent the ending period</li>
                <li>Data updates at the top of each hour</li>
            </ul>
        </div>`,
        border: false
    });

    // Main application panel - replaces Viewport for constrained layout
    // eslint-disable-next-line no-unused-vars
    const mainPanel = new Ext.Panel({  // skipcq
        renderTo: 'extjs-container',
        layout: 'border',
        height: 600,
        border: true,
        items: [
            {
                region: 'west',
                width: 220,
                collapsible: true,
                title: 'Settings & Info',
                layout: 'fit',
                items: [
                    {
                        xtype: 'panel',
                        layout: 'accordion',
                        items: [
                            {
                                title: 'Data Chooser',
                                items: [selectform]
                            },
                            {
                                title: 'Information',
                                items: [tp]
                            }
                        ]
                    }
                ]
            },
            gpanel
        ]
    });

});
