# Generate PyNGL resources necessary for a 'standardized' IEM plot, maybe!

import Ngl
import numpy
import mx.DateTime
import datetime
import tempfile
import os
import sys
from windrose.windrose import WindroseAxes
import matplotlib
import matplotlib.image as image
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import iemdb

# Define grid bounds 
IA_WEST  = -96.7
IA_EAST  = -90.1
IA_NORTH = 43.51
IA_SOUTH = 40.37
IA_NX    = 30
IA_NY    = 20
# Define grid bounds, midwest
MW_WEST  = -105.7
MW_EAST  = -80.1
MW_NORTH = 53.51
MW_SOUTH = 30.37
MW_NX    = 100
MW_NY    = 100
# Define grid bounds, CONUS
CONUS_WEST  = -126.0
CONUS_EAST  = -66.1
CONUS_NORTH = 50.51
CONUS_SOUTH = 24.0
CONUS_NX    = 140
CONUS_NY    = 140

def hilo_valplot(lons, lats, highs, lows, cfg):
    """
    Special case of having a value plot with a high and low value to 
    plot, which is common for some climate applications
    """
    tmpfp = tempfile.mktemp()

    cmap = numpy.array([[1., 1., 1.], [0., 0., 0.], [1., 0., 0.], \
                    [0., 0., 1.], [0., 1., 0.]], 'f')

    rlist = Ngl.Resources()
    rlist.wkColorMap = cmap
    #rlist.wkOrientation = "landscape"
    wks = Ngl.open_wks("ps", tmpfp, rlist)

    res = iowa()
    res.mpOutlineDrawOrder = "PreDraw"
    plot = Ngl.map(wks, res)
    for key in cfg.keys():
        if key == 'wkColorMap' or key[0] == "_":
            continue
        setattr(res, key, cfg[key])

    txres              = Ngl.Resources()
    txres.txFontHeightF = 0.016
    txres.txFontColor   = "red"
    txres.txJust        = "BottomRight"
    for i in range(len(lons)):
        Ngl.add_text(wks, plot, cfg["_format"] % highs[i], 
                      lons[i], lats[i],txres)

    txres              = Ngl.Resources()
    txres.txFontHeightF = 0.016
    txres.txFontColor   = "blue"
    txres.txJust        = "TopRight"
    for i in range(len(lons)):
        Ngl.add_text(wks, plot, cfg["_format"] % lows[i], 
                      lons[i], lats[i],txres)

    if cfg.has_key("_labels"):
        txres               = Ngl.Resources()
        txres.txFontHeightF = 0.008
        txres.txJust        = "CenterLeft"
        txres.txFontColor   = 1
        for i in range(len(lons)):
            Ngl.add_text(wks, plot, cfg["_labels"][i], 
                     lons[i], lats[i],txres)

    watermark(wks)
    manual_title(wks, cfg)
    vpbox(wks)
    Ngl.draw(plot)
    Ngl.frame(wks)
    del wks

    return tmpfp

def fit43(xmin, ymin, xmax, ymax, buffer=0):
    """
    Fit the bounds into an approximate 4x3 frame
    """
    desired = 6.1/3.  # Slightly over, due to Lambert Projection
    deltax = xmax - xmin 
    xavg = (xmax+xmin)/2.0
    deltay = ymax - ymin
    yavg = (ymax+ymin)/2.0
    aspect = deltax / deltay
    if aspect > desired:  # Need to vertically stretch!
        ymin = yavg - (deltax / desired * .5)
        ymax = yavg + (deltax / desired * .5)
    if aspect <= desired:  # Need to horizontally stretch!
        xmin = xavg - (deltay * desired * .5)
        xmax = xavg + (deltay * desired * .5)

    return [xmin - (buffer * desired), ymin - buffer,
           xmax + (buffer * desired), ymax + buffer]

def simple_valplot(lons, lats, vals, cfg):
    """
    Generate a simple plot of values on a map!
    """
    tmpfp = tempfile.mktemp()

    rlist = Ngl.Resources()
    if cfg.has_key("wkColorMap"):
        rlist.wkColorMap = cfg['wkColorMap']
    #rlist.wkOrientation = "landscape"

    # Create Workstation
    wks = Ngl.open_wks( "ps",tmpfp,rlist)

    res = iowa()
    if cfg.has_key("_spatialDataLimiter"):
        xmin, ymin, xmax, ymax = [ min(lons), min(lats), 
                                        max(lons), max(lats) ]
        res.mpMinLonF    = xmin - 0.25
        res.mpMaxLonF    = xmax + 0.25
        res.mpMinLatF    = ymin - 0.25
        res.mpMaxLatF    = ymax + 0.25
        res.mpCenterLonF = (xmax + xmin)/2.0  # Central Longitude
        res.mpCenterLatF = (ymax + ymin)/2.0  # Central Latitude
    res.mpOutlineDrawOrder = "PreDraw"
    res.mpUSStateLineColor = 10
    res.mpNationalLineColor = 10

    for key in cfg.keys():
        if key == 'wkColorMap' or key[0] == "_":
            continue
        setattr(res, key, cfg[key])

    plot = Ngl.map(wks, res)
    if cfg.has_key("_stationplot"):
        Ngl.wmsetp("col", 1)
        Ngl.wmsetp("ezf",1)
        if cfg.has_key("_removeskyc"):
            Ngl.wmsetp("WBC", 0.001) # Get rid of sky coverage
            Ngl.wmsetp("WBF", 0) # Put barb at center, no sky coverage
            Ngl.wmsetp("WBR", 0.001) # Size of calm circle
        #Ngl.wmsetp("WBL", 0.18) # Size of labels
        #Ngl.wmsetp("WBS", 0.029) # Size of wind barb shaft
        Ngl.wmstnm(wks, lats, lons, vals)
    else:
        txres              = Ngl.Resources()
        txres.txFontHeightF = 0.014
        txres.txJust        = "BottomCenter"
        for i in range(len(lons)):
            Ngl.add_text(wks, plot, cfg["_format"] % vals[i], 
                      lons[i], lats[i],txres)
    if cfg.has_key("_labels"):
        txres               = Ngl.Resources()
        txres.txFontHeightF = 0.008
        txres.txJust        = "TopCenter"
        txres.txFontColor   = 14
        for i in range(len(lons)):
            Ngl.add_text(wks, plot, cfg["_labels"][i], 
                     lons[i], lats[i],txres)

    watermark(wks)
    manual_title(wks, cfg)
    Ngl.draw(plot)
    vpbox(wks)
    Ngl.frame(wks)
    del wks

    return tmpfp

    vpbox(wks)
def simple_grid_fill(xaxis, yaxis, grid, cfg):
    """
    Generate a simple plot, but we already have the data!
    """
    tmpfp = tempfile.mktemp()
    rlist = Ngl.Resources()
    if cfg.has_key("wkColorMap"):
        rlist.wkColorMap = cfg['wkColorMap']
    #rlist.wkOrientation = "landscape"

    # Create Workstation
    wks = Ngl.open_wks( "ps",tmpfp,rlist)
    if cfg.has_key("_conus"):
        res = conus()
    elif cfg.has_key("_midwest"):
        res = midwest()
    else:
        res = iowa2()

    if cfg.has_key("_MaskZero"):
        mask = numpy.where( grid <= 0.01, True, False)
        grid = numpy.ma.array(grid, mask=mask)
 
    for key in cfg.keys():
        if key == 'wkColorMap' or key[0] == "_":
            continue
        setattr(res, key, cfg[key])
    res.sfXArray = xaxis
    res.sfYArray = yaxis
    # Generate Contour
    contour = Ngl.contour_map(wks,grid,res)

#    if cfg.has_key("_showvalues") and cfg['_showvalues']:
#        txres              = Ngl.Resources()
#        txres.txFontHeightF = 0.012
#        for i in range(len(xaxis)):
#            if cfg.has_key("_valuemask") and cfg['_valuemask'][i] is False:
#                continue
#            Ngl.add_text(wks, contour, cfg["_format"] % vals[i], 
#                     lons[i], lats[i],txres)


    Ngl.draw(contour)

    watermark(wks)
    manual_title(wks, cfg)
    Ngl.frame(wks)
    del wks

    return tmpfp

def simple_contour(lons, lats, vals, cfg):
    """
    Generate a simple contour plot, okay 
    """
    tmpfp = tempfile.mktemp()
    rlist = Ngl.Resources()
    if cfg.has_key("wkColorMap"):
        rlist.wkColorMap = cfg['wkColorMap']
    #rlist.wkOrientation = "landscape"

    # Create Workstation
    wks = Ngl.open_wks( "ps",tmpfp,rlist)
 
    # Create Analysis
    if cfg.has_key("_conus"):
        analysis, res = grid_conus(lons, lats, vals)
    elif cfg.has_key("_midwest"):
        analysis, res = grid_midwest(lons, lats, vals)
    else:
        analysis, res = grid_iowa(lons, lats, vals)
    analysis = numpy.transpose(analysis)

    for key in cfg.keys():
        if key == 'wkColorMap' or key[0] == "_":
            continue
        setattr(res, key, cfg[key])
    if cfg.has_key("_MaskZero"):
        mask = numpy.where( analysis <= 0.02, True, False)
        analysis = numpy.ma.array(analysis, mask=mask)

    # Generate Contour
    contour = Ngl.contour_map(wks,analysis,res)

    if cfg.has_key("_showvalues") and cfg['_showvalues']:
        txres              = Ngl.Resources()
        txres.txFontHeightF = 0.012
        for i in range(len(lons)):
            if cfg.has_key("_valuemask") and cfg['_valuemask'][i] is False:
                continue
            Ngl.add_text(wks, contour, cfg["_format"] % vals[i], 
                     lons[i], lats[i],txres)

    Ngl.draw( contour )

    watermark(wks)
    manual_title(wks, cfg)
    vpbox(wks)
    Ngl.frame(wks)
    del wks
    return tmpfp

def vpbox(wks):
    """ Draw a box around the viewport! """
    xbox = [0.1,0.9,0.9,0.1,0.1]
    ybox = [0.8,0.8,0.2,0.2,0.8]
    res = Ngl.Resources()
    res.gsLineColor = "NavyBlue" 
    res.gsLineThicknessF = 1.5
    Ngl.polyline_ndc(wks,xbox,ybox,res)


def manual_title(wks, cfg):
    """ Manually place a title """
    if cfg.has_key("_title"):
        txres = Ngl.Resources()
        txres.txFontHeightF = 0.02
        txres.txJust        = "CenterLeft"
        Ngl.text_ndc(wks, cfg["_title"], .11, .834, txres)
        del txres
    if cfg.has_key("_valid"):
        txres = Ngl.Resources()
        txres.txFontHeightF = 0.013
        txres.txJust        = "CenterLeft"
        Ngl.text_ndc(wks, "Map Valid: "+ cfg["_valid"], .11, .815, txres)
        del txres

def watermark(wks):
    txres              = Ngl.Resources()
    txres.txFontHeightF = 0.016
    txres.txJust = "CenterLeft"
    lstring = "Iowa Environmental Mesonet"
    Ngl.text_ndc(wks, lstring,.11,.186,txres)

    lstring = "Map Generated %s" % (mx.DateTime.now().strftime("%d %b %Y %-I:%M %p"),)
    txres.txFontHeightF = 0.010
    Ngl.text_ndc(wks, lstring,.11,.17,txres)

def grid_midwest(lons, lats, vals):
    """
    Convience routine to do a simple grid for MidWest
    @return numpy grid of values and plot res
    """
    delx = (MW_EAST - MW_WEST) / (MW_NX - 1)
    dely = (MW_NORTH - MW_SOUTH) / (MW_NY - 1)
    # Create axis
    xaxis = MW_WEST + delx * numpy.arange(0, MW_NX)
    yaxis = MW_SOUTH + dely * numpy.arange(0, MW_NY)
    # Create the analysis
    analysis = Ngl.natgrid(lons, lats, vals, xaxis, yaxis)

    # Setup res
    res = midwest()

    res.sfXCStartV = min(xaxis)
    res.sfXCEndV   = max(xaxis)
    res.sfYCStartV = min(yaxis)
    res.sfYCEndV   = max(yaxis)

    return analysis, res

def grid_conus(lons, lats, vals):
    """
    Convience routine to do a simple grid for CONUS
    @return numpy grid of values and plot res
    """
    delx = (CONUS_EAST - CONUS_WEST) / (CONUS_NX - 1)
    dely = (CONUS_NORTH - CONUS_SOUTH) / (CONUS_NY - 1)
    # Create axis
    xaxis = CONUS_WEST + delx * numpy.arange(0, CONUS_NX)
    yaxis = CONUS_SOUTH + dely * numpy.arange(0, CONUS_NY)
    # Create the analysis
    analysis = Ngl.natgrid(lons, lats, vals, xaxis, yaxis)

    # Setup res
    res = conus()

    res.sfXCStartV = min(xaxis)
    res.sfXCEndV   = max(xaxis)
    res.sfYCStartV = min(yaxis)
    res.sfYCEndV   = max(yaxis)
    
    return analysis, res


def grid_iowa(lons, lats, vals):
    """
    Convience routine to do a simple grid for Iowa
    @return numpy grid of values and plot res
    """
    delx = (IA_EAST - IA_WEST) / (IA_NX - 1)
    dely = (IA_NORTH - IA_SOUTH) / (IA_NY - 1)
    # Create axis
    xaxis = IA_WEST + delx * numpy.arange(0, IA_NX)
    yaxis = IA_SOUTH + dely * numpy.arange(0, IA_NY)
    # Create the analysis
    analysis = Ngl.natgrid(lons, lats, vals, xaxis, yaxis)

    # Setup res
    res = iowa2()

    res.sfXCStartV = min(xaxis)
    res.sfXCEndV   = max(xaxis)
    res.sfYCStartV = min(yaxis)
    res.sfYCEndV   = max(yaxis)

    return analysis, res

def iowa2():
    res = iowa()
    #_____________ LABEL BAR STUFF __________________________
    res.lbAutoManage       = False           # Let me drive!
    res.lbOrientation      = "Vertical"      # Draw it vertically
    res.lbTitleString      = "lbTitleString" # Default legend
    res.lbTitlePosition    = "Bottom"          # Place title on the left
    res.lbTitleOn          = True            # We want a title, please
    #res.lbTitleAngleF      = 90.0            # Rotate the title?
    #res.lbTitleDirection   = "Across"        # Make it appear rotated?
    res.lbPerimOn          = False            # Include a box aroundit
    res.lbPerimThicknessF  = 1.0             # Thicker line?
    #res.lbBoxMinorExtentF  = 0.15             # Narrower boxes
    res.lbTitleFontHeightF = 0.012
    res.lbLabelFontHeightF = 0.012
    res.lbRightMarginF    = 0.01
    res.lbLeftMarginF       = -0.02
    res.lbTitleExtentF     = 0.1

    #______________ Contour Defaults _______________________
    res.cnFillOn         = True    # filled contours
    res.cnInfoLabelOn    = False   # No information label
    res.cnLineLabelsOn   = False   # No line labels
    res.cnLinesOn        = False   # No contour lines
    res.cnFillDrawOrder  = "Predraw"       # Draw contour first!

    res.pmLabelBarHeightF = 0.5
    res.pmLabelBarWidthF = 0.05
    res.pmLabelBarKeepAspect = False
    res.pmLabelBarSide = "Right"

    res.mpFillOn                = True            # Draw map for sure
    res.mpFillAreaSpecifiers    = ["Conterminous US",]  # Draw the US
    res.mpSpecifiedFillColors   = [0,]            # Draw in white
    res.mpAreaMaskingOn         = True            # Mask by Iowa
    res.mpMaskAreaSpecifiers    = ["Conterminous US : Iowa",]

    return res


def iowa():
    """ Return Ngl resources for a standard Iowa plot """

    res = Ngl.Resources()
    res.nglFrame              = False        # and this
    res.nglDraw               = False        # Defaults this

    res.pmTickMarkDisplayMode = "Never"      # Turn off annoying ticks

    # Setup the viewport
    """
 0.1,0.8               0.9,0.8
    x                     x
        width : 0.8
        height: 0.6
 0.1,0.2               0.9,0.2
    x                     x
    """
    res.nglMaximize         = False      # Prevent funky things
    res.vpWidthF            = 0.8       # Default width of map?
    res.vpHeightF           = 0.6        # Go vertical
    res.nglPaperOrientation = "landscape" # smile
    res.vpXF                = 0.1        # Make Math easier
    res.vpYF                = 0.8        # 

    #____________ MAP STUFF ______________________
    res.mpProjection = "LambertEqualArea"   # Display projection
    res.mpCenterLonF = -93.5                # Central Longitude
    res.mpCenterLatF = 42.0                 # Central Latitude
    res.mpLimitMode  = "LatLon"             # Display bounds
    xmin, ymin, xmax, ymax = [-96.7, 40.3, -90.1, 43.6]
    res.mpMinLonF    = xmin
    res.mpMaxLonF    = xmax
    res.mpMinLatF    = ymin
    res.mpMaxLatF    = ymax
    res.mpPerimOn    = False               # Draw Border around Map
    res.mpDataBaseVersion       = "MediumRes"     # Don't need hires coast
    res.mpDataSetName           = "Earth..2"      # includes counties
    res.mpGridAndLimbOn         = False           # Annoying
    res.mpUSStateLineThicknessF = 3               # Outline States
    res.mpOutlineOn             = True           # Draw map for sure
    res.mpOutlineBoundarySets   = "NoBoundaries" # What not to draw
    res.mpOutlineSpecifiers     = ["Conterminous US : Iowa : Counties",]
    res.mpShapeMode = "FreeAspect"

    return res

def conus():
    """ Return Ngl resources for a standard MidWest plot """

    res = Ngl.Resources()
    res.nglFrame              = False        # and this
    res.nglDraw               = False        # Defaults this

    res.pmTickMarkDisplayMode = "Never"      # Turn off annoying ticks

    # Setup the view
    res.nglMaximize         = False      # Prevent funky things
    res.vpWidthF            = 0.8       # Default width of map?
    res.vpHeightF           = 0.8        # Go vertical
    res.nglPaperOrientation = "landscape"
    res.vpXF                = 0.1        # Make Math easier
    res.vpYF                = 0.9        # 

    #____________ MAP STUFF ______________________
    res.mpProjection = "LambertConformal"   # Display projection
    res.mpLambertParallel1F    = 33.0               
    res.mpLambertParallel2F    = 45.0
    res.mpLambertMeridianF     = -95.0            
    res.mpLimitMode            = "LatLon"
    res.mpMinLatF              = 24.0                
    res.mpMaxLatF              = 50.0              
    res.mpMinLonF              = -119.0          
    res.mpMaxLonF              = -74.0  
    
    res.mpPerimOn    = False                # Draw Border around Map
    res.mpDataBaseVersion       = "MediumRes"     # Don't need hires coast
    res.mpDataSetName           = "Earth..2"      # includes counties
    res.mpGridAndLimbOn         = False           # Annoying
    res.mpUSStateLineThicknessF = 1               # Outline States

    res.mpOutlineOn             = True           # Draw map for sure
    res.mpOutlineBoundarySets   = "USStates" # What not to draw
    #res.mpOutlineSpecifiers     = ["Conterminous US",
    #                           ]
    #res.mpShapeMode = "FreeAspect"

    #_____________ LABEL BAR STUFF __________________________
    res.lbAutoManage       = False           # Let me drive!
    res.lbOrientation      = "Vertical"      # Draw it vertically
    res.lbTitleString      = "lbTitleString" # Default legend
    res.lbTitlePosition    = "Bottom"          # Place title on the left
    res.lbTitleOn          = True            # We want a title, please
    #res.lbTitleAngleF      = 90.0            # Rotate the title?
    #res.lbTitleDirection   = "Across"        # Make it appear rotated?
    res.lbPerimOn          = False            # Include a box aroundit
    res.lbPerimThicknessF  = 1.0             # Thicker line?
    res.lbBoxMinorExtentF  = 0.2             # Narrower boxes
    res.lbTitleFontHeightF = 0.016
    res.lbLabelFontHeightF = 0.016
    #res.lbRightMarginF    = -0.3
    #res.lbLeftMarginF       = -0.3
    res.lbTitleExtentF     = 0.1

    #______________ Contour Defaults _______________________
    res.cnFillOn         = True    # filled contours
    res.cnInfoLabelOn    = False   # No information label
    res.cnLineLabelsOn   = False   # No line labels
    res.cnLinesOn        = False   # No contour lines
    res.cnFillDrawOrder  = "Predraw"       # Draw contour first!

    res.pmLabelBarHeightF = 0.4
    res.pmLabelBarWidthF = 0.06
    res.pmLabelBarKeepAspect = True
    res.pmLabelBarSide = "Right"

    res.mpFillOn                = True            # Draw map for sure
    res.mpFillAreaSpecifiers    = ["land","water"]  # Draw the US
    res.mpFillBoundarySets   = "NoBoundaries" # What not to draw
    res.mpSpecifiedFillColors   = [0,0]            # Draw in white
    res.mpAreaMaskingOn         = True            # Mask by Iowa
    res.mpMaskAreaSpecifiers    = ["Conterminous US",
                                   ]


    return res



def midwest():
    """ Return Ngl resources for a standard MidWest plot """

    res = Ngl.Resources()
    res.nglFrame              = False        # and this
    res.nglDraw               = False        # Defaults this

    res.pmTickMarkDisplayMode = "Never"      # Turn off annoying ticks

    # Setup the view
    res.nglMaximize         = False      # Prevent funky things
    res.vpWidthF            = 0.8       # Default width of map?
    res.vpHeightF           = 0.6        # Go vertical
    res.nglPaperOrientation = "landscape"
    res.vpXF                = 0.1        # Make Math easier
    res.vpYF                = 0.8        # 

    #____________ MAP STUFF ______________________
    res.mpProjection = "LambertEqualArea"   # Display projection
    res.mpCenterLonF = -93.5                # Central Longitude
    res.mpCenterLatF = 42.0                 # Central Latitude
    res.mpLimitMode  = "LatLon"             # Display bounds 
    xmin, ymin, xmax, ymax = [-104., 35.9, -82.4, 49.0]
    res.mpMinLonF    = xmin                # West
    res.mpMaxLonF    = xmax                # East
    res.mpMinLatF    = ymin                 # South
    res.mpMaxLatF    = ymax                 # North
    res.mpPerimOn    = False                # Draw Border around Map
    res.mpDataBaseVersion       = "MediumRes"     # Don't need hires coast
    res.mpDataSetName           = "Earth..2"      # includes counties
    res.mpGridAndLimbOn         = False           # Annoying
    res.mpUSStateLineThicknessF = 3               # Outline States

    res.mpOutlineOn             = True           # Draw map for sure
    res.mpOutlineBoundarySets   = "NoBoundaries" # What not to draw
    res.mpOutlineSpecifiers     = ["Conterminous US : Iowa",
                               "Conterminous US : Illinois",
                               "Conterminous US : Indiana",
                               "Conterminous US : Wisconsin",
                               "Conterminous US : Michigan",
                               "Conterminous US : Minnesota",
                               "Conterminous US : South Dakota",
                               "Conterminous US : North Dakota",
                               "Conterminous US : Nebraska",
                               "Conterminous US : Kansas",
                               "Conterminous US : Missouri",
                               ]
    res.mpShapeMode = "FreeAspect"

    #_____________ LABEL BAR STUFF __________________________
    res.lbAutoManage       = False           # Let me drive!
    res.lbOrientation      = "Vertical"      # Draw it vertically
    res.lbTitleString      = "lbTitleString" # Default legend
    res.lbTitlePosition    = "Bottom"          # Place title on the left
    res.lbTitleOn          = True            # We want a title, please
    #res.lbTitleAngleF      = 90.0            # Rotate the title?
    #res.lbTitleDirection   = "Across"        # Make it appear rotated?
    res.lbPerimOn          = False            # Include a box aroundit
    res.lbPerimThicknessF  = 1.0             # Thicker line?
    res.lbBoxMinorExtentF  = 0.2             # Narrower boxes
    res.lbTitleFontHeightF = 0.016
    res.lbLabelFontHeightF = 0.016
    #res.lbRightMarginF    = -0.3
    #res.lbLeftMarginF       = -0.3
    res.lbTitleExtentF     = 0.1

    #______________ Contour Defaults _______________________
    res.cnFillOn         = True    # filled contours
    res.cnInfoLabelOn    = False   # No information label
    res.cnLineLabelsOn   = False   # No line labels
    res.cnLinesOn        = False   # No contour lines
    res.cnFillDrawOrder  = "Predraw"       # Draw contour first!

    res.pmLabelBarHeightF = 0.4
    res.pmLabelBarWidthF = 0.06
    res.pmLabelBarKeepAspect = True
    res.pmLabelBarSide = "Right"

    res.mpFillOn                = True            # Draw map for sure
    res.mpFillAreaSpecifiers    = ["land","water"]  # Draw the US
    res.mpFillBoundarySets   = "NoBoundaries" # What not to draw
    res.mpSpecifiedFillColors   = [0,0]            # Draw in white
    res.mpAreaMaskingOn         = True            # Mask by Iowa
    res.mpMaskAreaSpecifiers    = ["Conterminous US : Iowa",
                                   "Conterminous US : Illinois",
                                   "Conterminous US : Indiana",
                                   "Conterminous US : Wisconsin",
                                   "Conterminous US : Minnesota",
                                   "Conterminous US : Missouri",
                                   "Conterminous US : Nebraska",
                                   "Conterminous US : Kansas",
                                   "Conterminous US : Michigan",
                                   "Conterminous US : South Dakota",
                                   "Conterminous US : North Dakota",
                                   ]


    return res

def makefeature(tmpfp):
    """
    Helper function to pre generate the feature images based on this 
    generated PS file
    """
    if not os.path.isfile("%s.ps" % (tmpfp,)):
        print "File %s.ps is missing!" % (tmpfp,)
        return
    tomorrow = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=1)
    # Step 1. Convert to Big PNG
    cmd = "convert -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 -depth 8 -colors 256 +repage %s.ps %s.png" % (tmpfp, tomorrow.strftime("%y%m%d") )
    os.system( cmd )
    cmd = "convert -trim -border 5 -bordercolor '#fff' -resize 320x290 -density 80  +repage -depth 8 -colors 256 %s.ps %s_s.png" % (tmpfp, tomorrow.strftime("%y%m%d") )
    os.system( cmd )
    # Step 4: Cleanup
    os.remove("%s.ps" % (tmpfp,) )

def postprocess(tmpfp, pqstr, rotate=""):
    """
    Helper to postprocess the plot
    """
    if not os.path.isfile("%s.ps" % (tmpfp,)):
        print "File %s.ps is missing!" % (tmpfp,)
        return
    # Step 1. Convert to PNG
    cmd = "convert %s -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 -depth 8 -colors 256 +repage %s.ps %s.png" % (rotate, tmpfp, tmpfp)
    os.system( cmd )
    # Step 2: Send to LDM
    cmd = "/home/ldm/bin/pqinsert -p '%s' %s.png" % (pqstr, tmpfp)
    os.system( cmd )
    # Step 3: Show darly, if he is watching
    if os.environ['USER'] == 'akrherz':
        try:
            os.system("xv %s.png" % (tmpfp,))
        except:
            pass
    # Step 4: Cleanup
    os.remove("%s.png" % (tmpfp,) )
    os.remove("%s.ps" % (tmpfp,) )

def windrose(station, database='asos', fp=None, months=numpy.arange(1,13),
    hours=numpy.arange(0,24), sts=datetime.datetime(1900,1,1),
    ets=datetime.datetime(2050,1,1)):
    """
    Create a standard windrose plot that we can all happily use
    """
    # Query metadata
    db = iemdb.connect('mesosite', bypass=True)
    mcursor = db.cursor()
    mcursor.execute("""SELECT name from stations where id = %s""" ,(station,))
    row = mcursor.fetchall()
    sname = row[0][0]
    mcursor.close()
    db.close()

    # Query observations
    db = iemdb.connect(database, bypass=True)
    acursor = db.cursor()
    acursor.execute("""SELECT sknt, drct, valid from alldata WHERE station = %s
        and sknt >= 0 and drct >= 0 and valid > %s and valid < %s""", (
        station, sts, ets))
    sknt = []
    drct = []
    for row in acursor:
        if row[2].month not in months or row[2].hour not in hours:
           continue
        if len(sknt) == 0:
           minvalid = row[2]
           maxvalid = row[2]
        sknt.append( row[0] * 1.15 ) 
        drct.append( row[1] )
        if row[2] < minvalid:
            minvalid = row[2]
        if row[2] > minvalid:
            maxvalid = row[2]
    acursor.close()
    db.close()
    # Convert to numpy arrays
    sknt = numpy.array( sknt )
    drct = numpy.array( drct )
    # Generate figure
    fig = plt.figure(figsize=(6, 7), dpi=80, facecolor='w', edgecolor='w')
    rect = [0.1, 0.1, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    ax.bar(drct, sknt, normed=True, bins=(1,2,5,7,10,15,20), opening=0.8, edgecolor='white')
    #l = ax.legend(borderaxespad=-0.1)
    #plt.setp(l.get_texts(), fontsize=8)
    #ax.set_title("Ames [KAMW] Windrose Plot")
    handles = []
    for p in ax.patches_list[1:]:
        color = p.get_facecolor()
        handles.append( Rectangle((0, 0), 0.1, 0.3,
                    facecolor=color, edgecolor='black'))
    l = fig.legend( handles, ('2-5','5-7','7-10','10-15','15-20','20+') , loc=3,
     ncol=6, title='Wind Speed [mph]', mode=None, columnspacing=0.9, 
     handletextpad=0.45)
    plt.setp(l.get_texts(), fontsize=10)
    # Now we put some fancy debugging info on the plot
    tlimit = "Time Domain: "
    if len(hours) == 24 and len(months) == 12:
        tlimit = "All Year"
    if len(hours) < 24:
        for h in hours: 
            tlimit += "%s," % (datetime.datetime(2000,1,1,h).strftime("%I %P"),)
    if len(months) < 12:
        for h in months: 
            tlimit += "%s," % (datetime.datetime(2000,h,1).strftime("%b"),)
    label = "%s [%s] Windrose Plot\n[%s]\nPeriod of Record: %s - %s\nNumber of Obs: %s   Calm: %.1f%%   Avg Speed: %.1f mph" % (sname, station, tlimit,
        minvalid.strftime("%d %b %Y"), maxvalid.strftime("%d %b %Y"), 
        len(sknt), 
        numpy.sum( numpy.where(sknt < 2., 1., 0.)) / float(len(sknt)) * 100.,
        numpy.average(sknt))
    plt.gcf().text(0.17,0.89, label)
    # Make a logo
    im = image.imread('/var/www/htdocs/images/logo_small.png')
    #im[:,:,-1] = 0.8

    plt.figimage(im, 10, 625)

    if fp is not None:
        plt.savefig(fp)
    else:
        print "Content-Type: image/png\n"
        plt.savefig( sys.stdout, format='png' )
   
    del sknt, drct, im
