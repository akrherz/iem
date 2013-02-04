# Generate a report of duration of certain temperature thresholds

import mx.DateTime
import constants

import numpy as np

def wrap(cnt, s=None):
    if cnt > 0:
        return s or cnt
    else:
        return ""

# http://stackoverflow.com/questions/4494404
def contiguous_regions(condition):
    """Finds contiguous True regions of the boolean array "condition". Returns
    a 2D array where the first column is the start index of the region and the
    second column is the end index."""

    # Find the indicies of changes in "condition"
    d = np.diff(condition)
    idx, = d.nonzero() 

    # We need to start things after the change in "condition". Therefore, 
    # we'll shift the index by 1 to the right.
    idx += 1

    if condition[0]:
        # If the start of condition is True prepend a 0
        idx = np.r_[0, idx]

    if condition[-1]:
        # If the end of condition is True, append the length of the array
        idx = np.r_[idx, condition.size] # Edit

    # Reshape the result into two columns
    idx.shape = (-1,2)
    return idx

def write(mydb, out, rs, station):
    out.write("""# First occurance of record consecutive number of days 
# above or below a temperature threshold
""")
    out.write("#   %-27s %-27s  %-27s %-27s\n" % (" Low Cooler Than", 
     " Low Warmer Than", " High Cooler Than", " High Warmer Than") )
    out.write("%3s %5s %10s %10s %5s %10s %10s  %5s %10s %10s %5s %10s %10s\n" % (
      'TMP', 'DAYS', 'BEGIN DATE', 'END DATE',
      'DAYS', 'BEGIN DATE', 'END DATE',
      'DAYS', 'BEGIN DATE', 'END DATE',
      'DAYS', 'BEGIN DATE', 'END DATE') )

    highs = np.zeros( (len(rs),), 'f')
    lows = np.zeros( (len(rs),), 'f')
    for i in range(len(rs)):
        highs[i] = rs[i]['high']
        lows[i] = rs[i]['low']

    for thres in range(-20,100,2):
        
        condition = lows < thres
        max_bl = 0
        max_bl_ts = mx.DateTime.now()
        for start, stop in contiguous_regions(condition):
            if (stop - start) > max_bl:
                max_bl = int(stop - start)
                max_bl_ts = mx.DateTime.DateTime(constants.startyear(station),1,1) + mx.DateTime.RelativeDateTime(days=int(start))
    
        condition = lows >= thres
        max_al = 0
        max_al_ts = mx.DateTime.now()
        for start, stop in contiguous_regions(condition):
            if (stop - start) > max_al:
                max_al = int(stop - start)
                max_al_ts = mx.DateTime.DateTime(constants.startyear(station),1,1) + mx.DateTime.RelativeDateTime(days=int(start))

        condition = highs < thres
        max_bh = 0
        max_bh_ts = mx.DateTime.now()
        for start, stop in contiguous_regions(condition):
            if (stop - start) > max_bh:
                max_bh = int(stop - start)
                max_bh_ts = mx.DateTime.DateTime(constants.startyear(station),1,1) + mx.DateTime.RelativeDateTime(days=int(start))
    
        condition = highs >= thres
        max_ah = 0
        max_ah_ts = mx.DateTime.now()
        for start, stop in contiguous_regions(condition):
            if (stop - start) > max_ah:
                max_ah = int(stop - start)
                max_ah_ts = mx.DateTime.DateTime(constants.startyear(station),1,1) + mx.DateTime.RelativeDateTime(days=int(start))


        out.write("%3i %5s %10s %10s %5s %10s %10s  %5s %10s %10s %5s %10s %10s\n" % (
    thres, 
    wrap(max_bl), 
    wrap(max_bl, (max_bl_ts - mx.DateTime.RelativeDateTime(days=max_bl)).strftime("%m/%d/%Y")), 
    wrap(max_bl, max_bl_ts.strftime("%m/%d/%Y") ),

    wrap(max_al), 
    wrap(max_al, (max_al_ts - mx.DateTime.RelativeDateTime(days=max_al)).strftime("%m/%d/%Y")), 
    wrap(max_al, max_al_ts.strftime("%m/%d/%Y") ),

    wrap(max_bh), 
    wrap(max_bh, (max_bh_ts - mx.DateTime.RelativeDateTime(days=max_bh)).strftime("%m/%d/%Y")), 
    wrap(max_bh, max_bh_ts.strftime("%m/%d/%Y") ),

    wrap(max_ah), 
    wrap(max_ah, (max_ah_ts - mx.DateTime.RelativeDateTime(days=max_ah)).strftime("%m/%d/%Y")), 
    wrap(max_ah, max_ah_ts.strftime("%m/%d/%Y") )
  ) )

    