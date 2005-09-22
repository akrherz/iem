import java.awt.*;
import java.net.*;
import java.io.*;
import java.util.*;
import netscape.javascript.*;
import com.sixlegs.image.png.*;

public class mapimage extends java.applet.Applet {
    String 	s=null;
    Image 	img, offScreenImage;
    int		jitter;
    int         x1=-100, y1=-100, x2=-100, y2=-100;
    double	imgminx, imgminy, imgmaxx, imgmaxy, cellsize=0;
    Dimension 	offScreenSize;
    Graphics 	offScreenGraphics;
    JSObject  	win;
    boolean	init=true;
    int		cursorSize=4;
    boolean     box=true;
    int         r=0, g=0, b=0;
    Color       c;

    MediaTracker tracker;

    public void init () {
	URL imgurl=null;
	
	tracker = new MediaTracker(this);

	// get the Navigator window handle
	win = JSObject.getWindow(this);
	
	jitter = atoi(getParameter("jitter"));

	s = getParameter("color");
	if(s != null) {
	    r = atoi(getToken(s,1));
	    g = atoi(getToken(s,2));
	    b = atoi(getToken(s,3));
	}
	c = new Color(r,g,b);
	
	// nab the image itself
	s = getParameter("image");
//        try {
//	  imgurl = new URL(s);
//	} catch(MalformedURLException e) {}
//	img = getImage(imgurl);

       try {
            imgurl = new URL(s);
       } catch(MalformedURLException e) {}
       try {
        PngImage png = new PngImage(imgurl);
        img = Toolkit.getDefaultToolkit().createImage(png);
       } catch (IOException e) { System.err.println(e); }

	tracker.addImage(img, 0);
    }
    
    public void boxOn () {
	box = true;
	return;
    }

    public void boxOff () {
	box = false;
	x2 = x1; // collapse
	y2 = y1;
	win.eval("SetImageBox(\"-1 -1 -1 -1\"); ");
	repaint();
	return;
    }

    public void newMap(String s) {
	URL imgurl=null;

	tracker.removeImage(img,0);

	try {
	    imgurl = new URL(s);
	} catch(MalformedURLException e) {
	    return;
	}
	img = getImage(imgurl);

	tracker.addImage(img, 0);

	try { 
	  tracker.waitForID(0); // wait till it loads
	} catch (InterruptedException e) {
	  return;
	}
	
	// reinitialize the cursor position
	x1 = x2 = (offScreenSize.width-1)/2; // cleaner way?
	y1 = y2 = (offScreenSize.height-1)/2;
	win.eval("SetImageBox(\"" + Math.min(x1,x2) + " " + Math.min(y1,y2) + " " + Math.max(x1,x2) + " " + Math.max(y1,y2) + "\"); ");
	win.eval("SetImageXY(\"" + x1 + " " + y1 + "\"); ");

        repaint();
	return;
    }

    static String getToken(String s, int n) {
	int i;
	StringTokenizer st = new StringTokenizer(s);
	
	if(st.countTokens() < n)
	    return(null);
	
	for(i=1;i<n;i++)
	    st.nextToken();
	
	return(st.nextToken());
    }

    static int atoi(String s) {
	int n = 0;
	
	try {
	    n = new Integer(s.trim()).intValue();
	} catch(NumberFormatException e) {}
	return(n);
    }
    
    static double atof(String s) {
	double n = 0.0;
	
	try {
	    n = new Double(s.trim()).doubleValue();
	} catch(NumberFormatException e) {}
	return(n);
    }
    
    public boolean mouseDown(Event e, int x, int y) {
	x1 = x;
	y1 = y;
	return true;
    }
    
    public boolean mouseDrag(Event e, int x, int y) {
	x2 = x;
	y2 = y;
	if(!box) {
	    x1 = x;
	    y1 = y;	    
	}
	repaint();
	return true;
    }
    
    public boolean mouseUp(Event e, int x, int y) {
	
	if(box) {
	    x2 = x;
	    y2 = y;
	    if ( x2 > img.getWidth(this)) { x2 = img.getWidth(this)-1; } 
	    if ( x2 < 0 ) { x2 = 0; } 
	    if ( y2 > img.getHeight(this)) { y2 = img.getHeight(this)-1; } 
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
	
	win.eval("SetImageBox(\"" + Math.min(x1,x2) + " " + Math.min(y1,y2) + " " + Math.max(x1,x2) + " " + Math.max(y1,y2) + "\"); ");
	win.eval("SetImageXY(\"" + x1 + " " + y1 + "\"); ");
	
	return true;
    }
    
    public void paint(Graphics g) {
	// draw the image
	g.drawImage(img,0,0,this);
	
	// draw the user defined rectangle or crosshair
	g.setColor(c);
	if((x1==x2) && (y1==y2)) {
	    g.drawLine((x2-cursorSize), y2, (x2+cursorSize), y2);
	    g.drawLine(x2, (y2-cursorSize), x2, (y2+cursorSize));
	} else {
	    g.drawRect(Math.min(x1,x2), Math.min(y1,y2), Math.abs(x1-x2), Math.abs(y1-y2));
	}
    }
    
    
    public void destroy () {}
    
    public void update (Graphics g) {
	Dimension d = size();
	if ((offScreenImage == null) || 
	    (d.width != offScreenSize.width) ||  
	    (d.height != offScreenSize.height)) {
	    offScreenImage = createImage(d.width, d.height);
	    offScreenSize = d;
	    offScreenGraphics = offScreenImage.getGraphics();
	} 
	offScreenGraphics.setColor(getBackground());
	offScreenGraphics.fillRect(0, 0, d.width, d.height);
	paint(offScreenGraphics);
	g.drawImage(offScreenImage, 0, 0, this);
    }   
}
