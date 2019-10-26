#!/usr/bin/env python
"""Loops the Iowa ETA plots"""

import cgi

import printHTML

htmlRoot = "https://mesonet.agron.iastate.edu/~mm5/current"


def main():
    form = cgi.FieldStorage()
    try:
        mapType = form.getfirst("mapType")
    except Exception:
        print("Hi")
    try:
        Fhour = form.getfirst("Fhour")
    except Exception:
        print("Hi")

    files = [
        (htmlRoot + Fhour + "/" + mapType + "F00.gif", "F00"),
        (htmlRoot + Fhour + "/" + mapType + "F03.gif", "F03"),
        (htmlRoot + Fhour + "/" + mapType + "F06.gif", "F06"),
        (htmlRoot + Fhour + "/" + mapType + "F09.gif", "F09"),
        (htmlRoot + Fhour + "/" + mapType + "F12.gif", "F12"),
        (htmlRoot + Fhour + "/" + mapType + "F15.gif", "F15"),
        (htmlRoot + Fhour + "/" + mapType + "F18.gif", "F18"),
        (htmlRoot + Fhour + "/" + mapType + "F21.gif", "F21"),
        (htmlRoot + Fhour + "/" + mapType + "F24.gif", "F24"),
        (htmlRoot + Fhour + "/" + mapType + "F27.gif", "F27"),
        (htmlRoot + Fhour + "/" + mapType + "F30.gif", "F30"),
        (htmlRoot + Fhour + "/" + mapType + "F33.gif", "F33"),
        (htmlRoot + Fhour + "/" + mapType + "F36.gif", "F36"),
        (htmlRoot + Fhour + "/" + mapType + "F39.gif", "F39"),
        (htmlRoot + Fhour + "/" + mapType + "F42.gif", "F42"),
        (htmlRoot + Fhour + "/" + mapType + "F45.gif", "F45"),
        (htmlRoot + Fhour + "/" + mapType + "F48.gif", "F48"),
    ]

    print("Content-type: text/html \n\n")
    print("<HTML><HEAD></HEAD>")

    printHTML.printTop()

    print("first_image = 1;")
    print("last_image = 17;")

    printHTML.printBot()

    print("theImages[0] = new Image();")
    print('theImages[0].src = "' + files[0][0] + '";')
    print("imageNum[0] = true;")
    print('myProg[0] = "F00";')

    printHTML.printBot15()

    for i in range(1, len(files)):
        print("theImages[" + str(i) + "] = new Image();")
        print("theImages[" + str(i) + '].src = "' + files[i][0] + '";')
        print("myProg[" + str(i) + '] = "' + files[i][1] + '";')

        print("imageNum[" + str(i) + "] = true;")
        print("document.animation.src = theImages[" + str(i) + "].src;")
        print("document.control_form.frame_nr.value = " + str(i) + ";")

    printHTML.printBot2()

    print('SRC="' + files[0][0] + '"')

    printHTML.printBot3()


if __name__ == "__main__":
    main()
