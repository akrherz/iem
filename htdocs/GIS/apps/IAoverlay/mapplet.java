//
// Mapplet applet is part of the MapServer client support
// package. - SDL -
//
// Paramters:
//    color int, int, int - color to use (rgb) for the selection rectangle.
//    jitter int - minimum size (in pixels) for a dragged box.
//    image string - url for the image to display, must be fully qualified.
//    thickness int - thickness (in pixels) of the dragged box.
//    box on/off - status for box drawing, default is on
//    verbose on/off - status for coordindate reporting (in pixels), default is off
//
// Public methods:
//    boxon - toggles box drawing on.
//    boxoff - toggles box drawing off.
//    swap(string) - displays the image loaded from the passed url. 

import java.applet.Applet;
import java.awt.*;
import java.awt.event.*;
import java.net.*;
import java.util.*;
import netscape.javascript.*;

class evalThread extends Thread {
    JSObject twindow;
    double tx1, tx2, ty1, ty2;
    boolean tdraw;
    String tname;

    public evalThread(JSObject window, String name, double x1, double y1, double x2, double y2, boolean draw) {
	twindow = window;
	tname = name;
	tx1 = x1;
	ty1 = y1;
	tx2 = x2;
	ty2 = y2;
	tdraw = draw;
    }

    public void run() {
	twindow.eval("mapplet_apply('" + tname + "'," + Math.min(tx1,tx2) + "," + Math.min(ty1,ty2) + "," + Math.max(tx1,tx2) + "," + Math.max(ty1,ty2) + ", " + tdraw + ");");
    }
}

public class mapplet extends Applet implements MouseListener, MouseMotionListener {
    String 	name;
    boolean     busy=false, box=true, init=true, verbose=false;
    Image 	img, busyimg=null;
    double      x1=-1, y1=-1, x2=-1, y2=-1;    
    int		jitter=5, cursorsize=4, thickness=1;

    Color       color=Color.red;

    JSObject  	window;

    Image       offScreenImage;
    Graphics 	offScreenGraphics;

    Dimension   screenSize;
    
    public void init () {
	StringTokenizer st;
	String 	s=null, t=null;
	URL url=null;

	screenSize = this.getSize(); // nab the applet size

	offScreenImage = createImage(screenSize.width, screenSize.height);
	offScreenGraphics = offScreenImage.getGraphics();
	
	// get the Navigator window handle
	window = JSObject.getWindow(this);

	s = getParameter("jitter");
	if(s != null)
	    jitter = Integer.parseInt(s);
	
	s = getParameter("color");
	if(s != null) {
	    color = getColorParameter(s);
	}
	
	s = getParameter("thickness");
	if(s != null)
	    thickness = Integer.parseInt(s);

	s = getParameter("cursorsize");
	if(s != null)
	    cursorsize = Integer.parseInt(s);

        s = getParameter("verbose");
	if(s != null) {
	    if(s.equalsIgnoreCase("on")) verbose = true;
	}

	s = getParameter("box");
	if(s != null) {
	    if(s.equalsIgnoreCase("off")) box = false;
	}

	name = getParameter("name");

	s = getParameter("busyimage");
	if(s != null) {
	    try {
		url = new URL(s);
	    } catch(MalformedURLException e) {
		window.eval("mapplet_error('" + name + "','Applet error. Malformed image URL.');");
		this.stop();
	    }
	    busyimg = getImage(url);
	}

	// nab the image itself
	s = getParameter("image");
        try {
	    url = new URL(s);
	} catch(MalformedURLException e) { 
	    window.eval("mapplet_error('" + name + "','Applet error. Malformed image URL.');");
	    this.stop();
	}
	img = getImage(url);
	
	// we want mouse events and mouse movement events
	addMouseListener(this);
	addMouseMotionListener(this);
    }

    private Color getColorParameter(String s) {
	StringTokenizer st;
	int r, g, b;
	
	// check if a pre-defined color is specified	
	if (s.equalsIgnoreCase("black"))
	    return(Color.black);
	if (s.equalsIgnoreCase("blue"))
	    return(Color.blue);
	if (s.equalsIgnoreCase("cyan"))
	    return(Color.cyan);
	if (s.equalsIgnoreCase("darkGray"))
	    return(Color.darkGray);
	if (s.equalsIgnoreCase("gray"))
	    return(Color.gray);
	if (s.equalsIgnoreCase("green"))
	    return(Color.green);
	if (s.equalsIgnoreCase("lightGray"))
	    return(Color.lightGray);
	if (s.equalsIgnoreCase("magenta"))
	    return(Color.magenta);
	if (s.equalsIgnoreCase("orange"))
	    return(Color.orange);
	if (s.equalsIgnoreCase("pink"))
	    return(Color.pink);
	if (s.equalsIgnoreCase("red"))
	    return(Color.red);
	if (s.equalsIgnoreCase("white"))
	    return(Color.white);
	if (s.equalsIgnoreCase("yellow"))
	    return(Color.yellow);

	// nope, must be an RGB triplet
	st = new StringTokenizer(s, ",");
	r = Integer.parseInt(st.nextToken());
	g = Integer.parseInt(st.nextToken());
	b = Integer.parseInt(st.nextToken());
	return(new Color(r,g,b));
  }

    public void boxon () {
	box = true;
	return;
    }
    
    public void boxoff () {
	box = false;
	x2 = x1; // collapse
	y2 = y1;
	
	repaint();

	new evalThread(window, name, x1, y1, x2, y2, false).start();
	
	return;
    }
    
    public void swap(String s) {
	URL url=null;
	MediaTracker tracker = new MediaTracker(this);
	
	busy = true;

	// reinitialize the cursor position
	x1 = x2 = (screenSize.width-1)/2.0;
	y1 = y2 = (screenSize.height-1)/2.0;
	
	if(busyimg != null)
	    repaint(); // show busy image

	// img.flush();
	   
	try {
	    url = new URL(s);
	} catch(MalformedURLException e) {
	    return;
	}
	
	img = getImage(url);
	tracker.addImage(img, 0);

	try { 
	  tracker.waitForID(0); // wait till it loads
	} catch (InterruptedException e) {
	  return;
	}
	
	busy = false;
	
        repaint();

	new evalThread(window, name, x1, y1, x2, y2, false).start();

	return;
    }

    //
    // Mouse event handlers
    //
    public void mouseClicked(MouseEvent e) { }
    public void mouseEntered(MouseEvent e) { }
    public void mouseExited(MouseEvent e) { 
	if(verbose) window.eval("javascript:mapplet_mouse_exited('" + name + "');");
    }

    public void mouseMoved(MouseEvent e) { 
        if(verbose) window.eval("javascript:mapplet_mouse_moved('" + name + "'," + e.getX() + "," + e.getY() + ");");
    }

    public void mousePressed(MouseEvent e) {
	x1 = x2 = e.getX();
	y1 = y2 = e.getY();
    }

    public void mouseDragged(MouseEvent e) {
	x2 = e.getX();
	y2 = e.getY();
	if(!box) {
	    x1 = x2;
	    y1 = y2;	    
	}
	repaint();
    }

    public void mouseReleased(MouseEvent e) { 	
	
	if(box) {
	    x2 = e.getX();
	    y2 = e.getY();
	    if ( x2 > screenSize.width) { x2 = screenSize.width-1; } 
	    if ( x2 < 0 ) { x2 = 0; } 
	    if ( y2 > screenSize.height) { y2 = screenSize.height-1; } 
	    if ( y2 < 0 ) { y2 = 0; } 
	    
	    // check to see if (x2,y2) forms a large enough rectangle
	    // to be considered a new extent or if the user is just a
	    // poor mouse clikcker
	    if((Math.abs(x1-x2) <= jitter) || (Math.abs(y1-y2) <= jitter)) {
		x2 = x1;
		y2 = y1;
	    }
	} else {
	    x2 = x1;
	    y2 = y1;
	}
	
	repaint();

	// this a time for a re-draw if the application so chooses
	if(!busy)
	    new evalThread(window, name, x1, y1, x2, y2, true).start();
    }
    
    public void paint(Graphics g) {
	int i;
	int x, y, w, h;
	Rectangle rect;
	Polygon poly;

	// draw the image
	offScreenGraphics.drawImage(img,0,0,this);	
	
	// draw the user defined rectangle or crosshair
	offScreenGraphics.setColor(color);
	if((x1==x2) && (y1==y2)) {
	    if(cursorsize > 0) {
	      offScreenGraphics.drawLine((int)(x2-cursorsize), (int)y2, (int)(x2+cursorsize), (int)y2);
	      offScreenGraphics.drawLine((int)x2, (int)(y2-cursorsize), (int)x2, (int)(y2+cursorsize));
	    }
	} else {
	    x = (int)Math.min(x1,x2);
	    y = (int)Math.min(y1,y2);
	    w = (int)Math.abs(x1-x2);
	    h = (int)Math.abs(y1-y2);
	    
	    for(i=0; i<thickness; i++)
		offScreenGraphics.drawRect(x+i, y+i, w-(2*i), h-(2*i));
	}
	
	if(busy && busyimg != null) {
	    x = screenSize.width/2 - busyimg.getWidth(this)/2;
	    y = screenSize.height/2 - busyimg.getHeight(this)/2;
	    offScreenGraphics.drawImage(busyimg,x,y,this);
	}

        g.drawImage(offScreenImage, 0, 0, this);
    }
    
    public void destroy () {}
    
    public void update (Graphics g) {
	paint(g);
    }   
}
