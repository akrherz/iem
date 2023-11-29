# Pick a sequential state
STATE=$(python util/pick_state.py)
# 1. Ensure database has entries between start and end dates
python climodat/check_database.py $STATE
# 2. Recompute sts, ets
python dbutil/compute_climate_sts.py ${STATE}CLIMATE
python dbutil/compute_coop_sts.py ${STATE}_COOP
# 3. Use ACIS
python climodat/use_acis.py $STATE
# 4. Look for any gaps that need estimating
python climodat/estimate_missing.py $STATE
# 5. Sync our COOP archives the same
python coop/use_acis.py --state=$STATE
# 6. Sync our IEMAccess (ASOS) archives
python asos/use_acis.py $STATE
