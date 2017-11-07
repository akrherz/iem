#!/usr/bin/env python
"""Python logic script to generate 1 plot or maybe a side by side."""

import cgi


def main():
    htmlBase = "https://mesonet.agron.iastate.edu/~mm5/Endow/Images/"
    print 'Content-type: text/html \n\n'
    form = cgi.FormContent()

    fdom0 = form["fdom"][0]
    fdata0 = form["fdata"][0]
    fweek0 = form["fweek"][0]
    if fdata0 == "1":
        img0ref = htmlBase+fdom0+"_"+fdata0+"_"+fweek0+".gif"
    else:
        img0ref = htmlBase+fdom0+"_"+fdata0+"_"+fweek0+".gif"

    print '<img src="'+img0ref+'">'


if __name__ == '__main__':
    main()
