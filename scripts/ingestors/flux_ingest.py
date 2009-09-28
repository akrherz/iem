
import csv, pg, mx.DateTime, traceback
other = pg.DB('other', 'iemdb')

# Figure out max valid times
maxts = {}
rs = other.query("SELECT station, max(valid) from flux%s GROUP by station" % (mx.DateTime.now().year - 1, ) ).dictresult()
for i in range(len(rs)):
  maxts[ rs[i]['station'] ] = mx.DateTime.strptime(rs[i]['max'][:16], '%Y-%m-%d %H:%M')
rs = other.query("SELECT station, max(valid) from flux%s GROUP by station" % (mx.DateTime.now().year, ) ).dictresult()
for i in range(len(rs)):
  maxts[ rs[i]['station'] ] = mx.DateTime.strptime(rs[i]['max'][:16], '%Y-%m-%d %H:%M')


cols_other = ["ts", "year", "jday", "hhmm", "bogus",
"Fc_wpl",
"LE_wpl",
"Hs",
"tau",
"u_star",
"cov_Uz_Uz",
"cov_Uz_Ux",
"cov_Uz_Uy",
"cov_Uz_co2",
"cov_Uz_h2o",
"cov_Uz_Ts",
"cov_Ux_Ux",
"cov_Ux_Uy",
"cov_Ux_co2",
"cov_Ux_h2o",
"cov_Ux_Ts",
"cov_Uy_Uy",
"cov_Uy_co2",
"cov_Uy_h2o",
"cov_Uy_Ts",
"cov_co2_co2",
"cov_h2o_h2o",
"cov_Ts_Ts",
"Ux_Avg",
"Uy_Avg",
"Uz_Avg",
"co2_Avg",
"h2o_Avg",
"Ts_Avg",
"rho_a_Avg",
"press_Avg",
"panel_temp_Avg",
"wnd_dir_compass",
"wnd_dir_csat3",
"wnd_spd",
"rslt_wnd_spd",
"batt_volt_Avg",
"std_wnd_dir",
"Fc_irga",
"LE_irga",
"co2_wpl_LE",
"co2_wpl_H",
"h2o_wpl_LE",
"h2o_wpl_H",
"h2o_hmp_Avg",
"t_hmp_Avg",
"SHF1_Avg",
"SHF2_Avg",
"SoilTC1_Avg",
"SoilTC2_Avg",
"SoilTC3_Avg",
"SoilTC4_Avg",
"IRT_can_Avg",
"IRT_cb_Avg",
"Incoming_SW",
"Outgoing_SW",
"Incoming_LW_TCor",
"Terrest_LW_TCor",
"Rn_short_Avg",
"Rn_long_Avg",
"Rn_total_Avg"]

cols_30ft = ["ts", "bogus", "bogus", "bogus", "bogus",
"Fc_wpl",
"LE_wpl",
"Hs",
"tau",
"u_star",
"cov_Uz_Uz",
"cov_Uz_Ux",
"cov_Uz_Uy",
"cov_Uz_co2",
"cov_Uz_h2o",
"cov_Uz_Ts",
"cov_Ux_Ux",
"cov_Ux_Uy",
"cov_Ux_co2",
"cov_Ux_h2o",
"cov_Ux_Ts",
"cov_Uy_Uy",
"cov_Uy_co2",
"cov_Uy_h2o",
"cov_Uy_Ts",
"cov_co2_co2",
"cov_h2o_h2o",
"cov_Ts_Ts",
"Ux_Avg",
"Uy_Avg",
"Uz_Avg",
"co2_Avg",
"h2o_Avg",
"Ts_Avg",
"rho_a_Avg",
"press_Avg",
"panel_temp_Avg",
"wnd_dir_compass",
"wnd_dir_csat3",
"wnd_spd",
"rslt_wnd_spd",
"batt_volt_Avg",
"std_wnd_dir",
"Fc_irga",
"LE_irga",
"co2_wpl_LE",
"co2_wpl_H",
"h2o_wpl_LE",
"h2o_wpl_H",
"h2o_hmp_Avg",
"t_hmp_Avg",
"PAR_avg",
"SolRad_Avg",
"Rain_Tot"]

fp = {'10.PRN': cols_other, '11.PRN': cols_other, '30FT.PRN': cols_30ft, 'NSP.PRN': cols_other, '110FT.PRN': cols_other}
sts = {'10.PRN': 'nstl10', '11.PRN': 'nstl11', '30FT.PRN': 'nstl30ft', 'NSP.PRN': 'nstlnsp', '110FT.PRN': 'nstl110'}


def c(v):
  if (v == "NAN" or v == "-INF" or v == "INF"):
    return None
  return v

cnt = 0
for file in fp.keys():

  for row in csv.reader( open('/home/mesonet/ot/ot0005/incoming/Fluxdata/%s' % (file,), 'rb') ):
    d = {}
    if (len(row) < 25):
      continue
    for i in range(len(row)):
      if (c(row[i])):
        d[ (fp[file][i]).lower() ] = c(row[i])

    d['valid'] = d['ts'] +"-06"
    try:
      ts = mx.DateTime.strptime(d['valid'][:16], '%Y-%m-%d %H:%M')
    except:
      print traceback.print_exc()
      print ':::%s:::' % (d['valid'],)
      continue
    if (maxts.has_key(sts[file]) and ts <=  maxts[ sts[file] ]):
      continue
    d['station'] = sts[file]
    del(d['ts'])
    del(d['bogus'])
    cnt += 1
    try:
      other.insert("flux%s" % (ts.year,) , d)
    except:
      print traceback.print_exc()

if (cnt < 50):
  print "Only %s records found!" % (cnt,)
