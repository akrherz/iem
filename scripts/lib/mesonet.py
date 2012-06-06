# Library of help functions
import math

def drct2dirTxt(dir):
  if (dir == None):
    return "N"
  dir = int(dir)
  if (dir >= 350 or dir < 13):
    return "N"
  elif (dir >= 13 and dir < 35):
    return "NNE"
  elif (dir >= 35 and dir < 57):
    return "NE"
  elif (dir >= 57 and dir < 80):
    return "ENE"
  elif (dir >= 80 and dir < 102):
    return "E"
  elif (dir >= 102 and dir < 127):
    return "ESE"
  elif (dir >= 127 and dir < 143):
    return "SE"
  elif (dir >= 143 and dir < 166):
    return "SSE"
  elif (dir >= 166 and dir < 190):
    return "S"
  elif (dir >= 190 and dir < 215):
    return "SSW"
  elif (dir >= 215 and dir < 237):
    return "SW"
  elif (dir >= 237 and dir < 260):
    return "WSW"
  elif (dir >= 260 and dir < 281):
    return "W"
  elif (dir >= 281 and dir < 304):
    return "WNW"
  elif (dir >= 304 and dir < 324):
    return "NW"
  elif (dir >= 324 and dir < 350):
    return "NNW"


def relh(tmpf, dwpf):
  if (tmpf == None or dwpf == None or tmpf == "M" or dwpf == "M" or tmpf == -99 or dwpf == -99):
    return "M"
  tmpc = f2c(tmpf)
  dwpc = f2c(dwpf)
  if (tmpc == dwpc):
    return 100.0
  e  = 6.112 * math.exp( (17.67 * dwpc) / (dwpc + 243.5));
  es  = 6.112 * math.exp( (17.67 * tmpc) / (tmpc + 243.5));
  relh = ( e / es ) * 100.00;
  return relh


def uv(sped,dir):
    """
    Compute the u and v components of the wind 
    @param wind speed in whatever units
    @param dir wind direction with zero as north
    @return u and v components
    """
    dirr = dir * math.pi / 180.00
    s = math.sin(dirr)
    c = math.cos(dirr)
    u = round(- sped * s, 2)
    v = round(- sped * c, 2)
    return u, v

def f2c(thisf):
    return 5.00/9.00 * (thisf - 32.00)

def c2f(thisc):
    return (9.00/5.00 * thisc) + 32.00

def k2f(thisk):
    return (9.00/5.00 * (thisk - 273.15)) + 32.00

def metar_tmpf(tmpf):
    """
    Convert a temperature in F to something metar wants
    """
    if tmpf is None:
        return 'MM'
    tmpc = f2c( tmpf )
    if tmpc < 0:
        return 'M%02.0f' % (0 - tmpc,)
    return '%02.0f' % (tmpc,)

def metar_tmpf_tgroup(tmpf):
    """
    Convert a temperature in F to something metar wants
    """
    if tmpf is None:
        return '////'
    tmpc = f2c( tmpf )
    if tmpc < 0:
        return '1%03.0f' % (0 - (tmpc*10.0),)
    return '0%03.0f' % ((tmpc*10.0),)

nwsli2state = {
"A2": "AK", "A1": "AL", "A4": "AR", "A3": "AZ", "C1": "CA", "C2": "CO",
"C3": "CT", "D2": "DC", "D1": "DE", "F1": "FL", "G1": "GA", "G5": "GM",
"H1": "HI", "I4": "IA", "I1": "ID", "I2": "IL", "I3": "IN", "K1": "KS",
"K2": "KY", "L1": "LA", "M3": "MA", "M2": "MD", "M1": "ME", "M4": "MI",
"M5": "MN", "M7": "MO", "M6": "MS", "M8": "MT", "N7": "NC",
"N8": "ND", "N1": "NE", "N3": "NH", "N4": "NJ", "N5": "NM", "N2": "NV",
"N6": "NY", "O1": "OH", "O2": "OK", "O3": "OR", "P5": "P1", "P6": "P2",
"P7": "P3", "P8": "P4", "P1": "PA", "R1": "RI", "S1": "SC", "S2": "SD",
"T1": "TN", "T2": "TX", "U1": "UT", "V2": "VA", "V1": "VT", "W1": "WA",
"W3": "WI", "W2": "WV", "W4": "WY", "Q1": "AB", "Q2": "BC", "Q3": "MB",
"B3": "NB", "N9": "NF", "S4": "NS", "Q5": "NW",
"Q6": "ON", "E1": "PE", "Q7": "PQ", "Q8": "SK",
"Q9": "YK", "A5": "AG", "B1": "BJ", "C6": "CH", "C8": "CI", "C7": "CL",
"C4": "CM", "C5": "CP", "D3": "DF", "D4": "DR",
"G2": "GJ", "G3": "GR", "H2": "HD", "J1": "JL", "C9": "MC", "R2": "MR",
"X1": "MX", "L3": "NL", "R3": "NR",
"O4": "OX", "P9": "PB", "S3": "SL", "S5": "SN", "S6": "SO", "T3": "TB",
"T5": "TL", "T4": "TP", "V4": "VC", "Y1": "YC", "Z1": "ZC", "E2": "ES",
"G4": "GT", "H3": "HO", "R5": "JA", "R6": "NU", "L3": "PO", "P4": "PR",
"R4": "RK", "V3": "VI",
"CH": "CH", "CL": "CL", "TP": "TP",
}
