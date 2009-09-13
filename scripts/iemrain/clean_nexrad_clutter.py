# Need a script to apply a filter around the ground clutter next to the
# NEXRADs

import mx.DateTime, lib, numpy

nexrads = [[41.60, -90.57], # DVN
           [41.72, -93.72], # DMX
           [41.32, -96.27]] # OAX, shifted 0.1 east

nc = lib.load_netcdf( mx.DateTime.DateTime(1997,5,1) )
precip = nc.variables['precipitation']

# Work on a daily basis
for i in range(31):
  for nexrad in nexrads:
    x,y = lib.nc_lalo2pt(nc, nexrad[0], nexrad[1] )
    #total = numpy.sum( precip[i*96:(i+1)*96,y-20:y+20,x-30:x+30], 0 )
    #
    # Compute the *median* 
    #goodVal = (numpy.sort( numpy.ravel(total) ))[300]
    #print "Median Val: %.2f Max Val: %.2f Avg: %.2f" % (goodVal, 
    #       numpy.max(total), numpy.average(total) )
    # Compute the ratio
    #ratio = goodVal / numpy.where(total > goodVal, total, goodVal)
    # Update precip totals!
    #precip[i*96:(i+1)*96,y-20:y+20,x-30:x+30] = precip[i*96:(i+1)*96,y-20:y+20,x-30:x+30] * ratio

    # Now, we need to brute force the numbers over the RADARs
    meanvalue = (precip[i*96:(i+1)*96,y-8,x-8] + 
       precip[i*96:(i+1)*96,y+8,x-8] + precip[i*96:(i+1)*96,y-8,x+8] +
       precip[i*96:(i+1)*96,y+8,x+8] ) / 4.0
    for k in range(len(meanvalue)):
      precip[(i*96)+k,y-5:y+5,x-5:x+5] = meanvalue[k]
nc.close()
