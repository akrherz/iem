#!/usr/bin/env python
""" Python logic script to generate 1 plot or maybe a side by side."""

import cgi


def main():
    """Go Main Go"""
    htmlBase = "https://mesonet.agron.iastate.edu/~mm5/current"
    print("Content-type: text/html \n\n")
    form = cgi.FieldStorage()

    run0 = form.getfirst("run0")
    data0 = form.getfirst("data0")
    fhour0 = form.getfirst("fhour0")
    if data0 == "eta24Prec":
        img0ref = htmlBase + run0 + "/" + data0 + ".gif"
    else:
        img0ref = htmlBase + run0 + "/" + data0 + "F" + fhour0 + ".gif"

    and1 = form.getfirst("and1")
    if and1 != "NO":
        run1 = form.getfirst("run1")
        data1 = form.getfirst("data1")
        fhour1 = form.getfirst("fhour1")
        if data1 == "eta24Prec":
            img1ref = htmlBase + run1 + "/" + data1 + ".gif"
        else:
            img1ref = htmlBase + run1 + "/" + data1 + "F" + fhour1 + ".gif"

        print("<TABLE><TR>")
        print("<TD>")
        print('<a href="' + img0ref + '">')
        print('<img src="' + img0ref + '" width="350">')
        print("</a></TD>")
        print("<TD>")
        print('<a href="' + img1ref + '">')
        print('<img src="' + img1ref + '" width="350">')
        print("</a></TD>")

        print("</TR></TABLE>")

    else:
        print('<img src="' + img0ref + '">')


if __name__ == "__main__":
    main()
