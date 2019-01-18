#!/usr/bin/env python
"""Loops the Iowa ETA plots."""

import cgi
import printHTML

htmlRoot = 'https://mesonet.agron.iastate.edu/~mm5/Endow/Images/'


def main():
    form = cgi.FieldStorage()
    try:
        fdom0 = form.getfirst("fdom")
        ffield0 = form.getfirst("ffield")
    except:
        print("Hi")

    files = [
        (htmlRoot+fdom0+"_"+ffield0+"_0.gif", "0"),
                        (htmlRoot+fdom0+"_"+ffield0+"_1.gif", "1"),
            (htmlRoot+fdom0+"_"+ffield0+"_2.gif", "2"),
            (htmlRoot+fdom0+"_"+ffield0+"_3.gif", "3"),
            (htmlRoot+fdom0+"_"+ffield0+"_4.gif", "4"),
            (htmlRoot+fdom0+"_"+ffield0+"_5.gif", "5"),
            (htmlRoot+fdom0+"_"+ffield0+"_6.gif", "6"),
            (htmlRoot+fdom0+"_"+ffield0+"_7.gif", "7"),
            (htmlRoot+fdom0+"_"+ffield0+"_8.gif", "8"),
            (htmlRoot+fdom0+"_"+ffield0+"_9.gif", "9"),
             (htmlRoot+fdom0+"_"+ffield0+"_10.gif", "10"),
                        (htmlRoot+fdom0+"_"+ffield0+"_11.gif", "11"),
                        (htmlRoot+fdom0+"_"+ffield0+"_12.gif", "12"),
                        (htmlRoot+fdom0+"_"+ffield0+"_13.gif", "13"),
                        (htmlRoot+fdom0+"_"+ffield0+"_14.gif", "14"),
                        (htmlRoot+fdom0+"_"+ffield0+"_15.gif", "15") ]

    print('Content-type: text/html \n\n')
    print('<HTML><HEAD></HEAD>')

    printHTML.printTop()

    print('first_image = 1;')
    print('last_image = 16;')

    printHTML.printBot()

    goodAnimation = 0

    print('theImages[0] = new Image();')
    print('theImages[0].src = "'+files[0][0]+'";')
    print('imageNum[0] = true;')
    print('myProg[0] = "0";')

    printHTML.printBot15()

    for i in range(1, len(files)):
        print('theImages['+str(i)+'] = new Image();')
        print('theImages['+str(i)+'].src = "'+files[i][0]+'";')
        print('myProg['+str(i)+'] = "'+files[i][1]+'";')

        print('imageNum['+str(i)+'] = true;')
        print('document.animation.src = theImages['+str(i)+'].src;')
        print('document.control_form.frame_nr.value = '+str(i)+';')

    printHTML.printBot2()

    print('SRC="'+files[0][0]+'"')

    printHTML.printBot3()


if __name__ == '__main__':
    main()
