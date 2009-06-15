# Generate PyNGL resources necessary for a 'standardized' IEM plot, maybe!

import Ngl
import numpy
import mx.DateTime

# Define grid bounds 
IA_WEST  = -96.7
IA_EAST  = -90.1
IA_NORTH = 43.51
IA_SOUTH = 40.37
IA_NX    = 30
IA_NY    = 20

def simple_valplot(lons, lats, vals, cfg):
    """
    Generate a simple plot of values on a map!
    """
    rlist = Ngl.Resources()
    if cfg.has_key("wkColorMap"):
        rlist.wkColorMap = cfg['wkColorMap']

    # Create Workstation
    wks = Ngl.open_wks( "ps","tmp",rlist)

    res = iowa()
    

    for key in cfg.keys():
        if key == 'wkColorMap' or key[0] == "_":
            continue
        setattr(res, key, cfg[key])

    plot = Ngl.map(wks, res)
    if cfg.has_key("_stationplot"):
        Ngl.wmsetp("col", 1)
        Ngl.wmsetp("ezf",1)
        Ngl.wmstnm(wks, lats, lons, vals)
    else:
        txres              = Ngl.Resources()
        txres.txFontHeightF = 0.016
        for i in range(len(lons)):
            Ngl.add_text(wks, plot, cfg["_format"] % vals[i], 
                     lons[i], lats[i],txres)
    watermark(wks)
    manual_title(wks, cfg)
    Ngl.draw(plot)
    Ngl.frame(wks)
    del wks


def simple_contour(lons, lats, vals, cfg):
    """
    Generate a simple contour plot, okay 
    """
    rlist = Ngl.Resources()
    if cfg.has_key("wkColorMap"):
        rlist.wkColorMap = cfg['wkColorMap']

    # Create Workstation
    wks = Ngl.open_wks( "ps","tmp",rlist)
 
    # Create Analysis
    analysis, res = grid_iowa(lons, lats, vals)
    analysis = numpy.transpose(analysis)

    for key in cfg.keys():
        if key == 'wkColorMap' or key[0] == "_":
            continue
        setattr(res, key, cfg[key])
    
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


    pres = Ngl.Resources()
    pres.nglFrame = False
    Ngl.panel(wks,[contour],[1,1], pres)

    watermark(wks)
    manual_title(wks, cfg)
    Ngl.frame(wks)
    del wks

def manual_title(wks, cfg):
    """ Manually place a title """
    if cfg.has_key("_title"):
        txres = Ngl.Resources()
        txres.txFontHeightF = 0.02
        txres.txJust        = "CenterLeft"
        Ngl.text_ndc(wks, cfg["_title"], .05, .80, txres)
        del txres
    if cfg.has_key("_valid"):
        txres = Ngl.Resources()
        txres.txFontHeightF = 0.013
        txres.txJust        = "CenterLeft"
        Ngl.text_ndc(wks, "Map Valid: "+ cfg["_valid"], .05, .78, txres)
        del txres

def watermark(wks):
    txres              = Ngl.Resources()
    txres.txFontHeightF = 0.016
    txres.txJust = "CenterLeft"
    lstring = "Iowa Environmental Mesonet"
    Ngl.text_ndc(wks, lstring,.05,.23,txres)

    lstring = "Map Generated %s" % (mx.DateTime.now().strftime("%d %b %Y %-I:%M %p"),)
    txres.txFontHeightF = 0.010
    Ngl.text_ndc(wks, lstring,.05,.21,txres)

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
    res = iowa()

    res.sfXCStartV = min(xaxis)
    res.sfXCEndV   = max(xaxis)
    res.sfYCStartV = min(yaxis)
    res.sfYCEndV   = max(yaxis)

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
    res.mpFillAreaSpecifiers    = ["Conterminous US",]  # Draw the US
    res.mpSpecifiedFillColors   = [0,]            # Draw in white
    res.mpAreaMaskingOn         = True            # Mask by Iowa
    res.mpMaskAreaSpecifiers    = ["Conterminous US : Iowa",]

    return analysis, res

def iowa():
    """ Return Ngl resources for a standard Iowa plot """

    res = Ngl.Resources()
    res.nglFrame              = False        # and this
    res.nglDraw               = False        # Defaults this

    res.pmTickMarkDisplayMode = "Never"      # Turn off annoying ticks

    # Setup the view
    res.nglMaximize         = False      # Prevent funky things
    res.vpWidthF            = 0.8       # Default width of map?
    res.vpHeightF           = 1.0        # Go vertical
    res.nglPaperOrientation = "portrait" # smile
    res.vpXF                = 0.0        # Make Math easier
    res.vpYF                = 1.0        # 

    #____________ MAP STUFF ______________________
    res.mpProjection = "LambertEqualArea"   # Display projection
    res.mpCenterLonF = -93.5                # Central Longitude
    res.mpCenterLatF = 42.0                 # Central Latitude
    res.mpLimitMode  = "LatLon"             # Display bounds  
    res.mpMinLonF    = -96.7                # West
    res.mpMaxLonF    = -90.1                # East
    res.mpMinLatF    = 40.3                 # South
    res.mpMaxLatF    = 43.7                 # North
    res.mpPerimOn    = False                # Draw Border around Map
    res.mpDataBaseVersion       = "MediumRes"     # Don't need hires coast
    res.mpDataSetName           = "Earth..2"      # includes counties
    res.mpGridAndLimbOn         = False           # Annoying
    res.mpUSStateLineThicknessF = 3               # Outline States

    res.mpOutlineOn             = True           # Draw map for sure
    res.mpOutlineBoundarySets   = "NoBoundaries" # What not to draw
    res.mpOutlineSpecifiers     = ["Conterminous US : Iowa : Counties",]


    return res
