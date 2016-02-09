import pyiem.cscap_utils as util

config = util.get_config()
ss = util.get_ssclient(config)

action = ss.Sheets.list_sheets(include_all=True)
for sheet in action.data:
    if not sheet.name.startswith("CSCAP Site Edits Needed_"):
        continue
    # print sheet.id, sheet.name
    s = ss.Sheets.get_sheet(sheet.id)
    titles = []
    for col in s.columns:
        titles.append(col.title)
    idx = titles.index('DONE')
    hits = 0
    cnt = 0
    for row in s.rows:
        if row.cells[idx].value is True:
            hits += 1
        cnt += 1
    print "%s,%s,%s,%.2f" % (sheet.name.split("_", 1)[1], hits, cnt,
                             hits / float(cnt) * 100.)
