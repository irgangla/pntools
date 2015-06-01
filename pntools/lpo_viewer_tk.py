#!/usr/bin/python3
# -*- coding_ utf-8 -*-

""" This program implements a viewer for the LPO data structure.

A LPO is a partial ordered set of events. If two events are ordered
this order is represented by an arrow. If there is an arrow form an
event a to an event b this means event b occurs after event a.

Usage: python lpo_viewer_tk.py [<lpo-file>]
"""

import math # calculation of intersection point (fabs, ...)
import sys # sys.argv
import partialorder # LPO parser and data structure
import os # demo file
from tkinter import Tk, Frame, Menu, Canvas, BOTH, LAST, filedialog # UI
from tkinter.ttk import Notebook # Tabs

class LpoView(Frame):
    """ This class implements a LPO widget.

    This class use a canvas to draw the Hasse diagram of a LPO.
    """

    def __init__(self, parent):
        """ This method creates a new, emtpy LpoView. """
        Frame.__init__(self, parent)
        self.__parent = parent
        self.__initUI()
        
        self.__lpo = None

    def __initUI(self):
        """ Set up user interface. """
        self.pack(fill=BOTH, expand=1)
        
        self.__canvas = Canvas(self) # canvas for LPO
        self.__canvas.pack(fill=BOTH, expand=1)
        # Scroll with mouse drag gestures
        self.__canvas.bind("<ButtonPress-1>", self.__scroll_start)
        self.__canvas.bind("<B1-Motion>", self.__scroll_move)

    def __scroll_start(self, event):
        """ Scroll LPO with mouse gestures: Start of scroll event. """
        self.__canvas.scan_mark(event.x, event.y)

    def __scroll_move(self, event):
        """ Scroll LPO with mouse gestures: Drag event. """
        self.__canvas.scan_dragto(event.x, event.y, gain=1)

        
    def showLpo(self, lpo_to_show):
        """ This method show the given LPO in this LpoView. """
        self.__lpo = lpo_to_show # set LPO reference
        self.__drawLpo() # create LPO graph

    def __drawLpo(self):
        """ This method draws the LPO. """
        # draw LPO arcs (arc layer is behind event layer)
        for arc in self.__lpo.arcs:
            # LPOs consists of all transitive arcs, the view shows only user defined arcs.
            if arc.user_drawn == True: 
                self.__drawArc(arc)

        # draw events
        for id, event in self.__lpo.events.items():
            self.__drawEvent(event)

    def __drawEvent(self, event):
        """ Draw the given event. """
        self.__canvas.create_rectangle(event.position[0] - 10, event.position[1] - 10, event.position[0] + 10, event.position[1] + 10, outline="#000", fill="#AAAAAA", width=2)
        self.__canvas.create_text(event.position[0], event.position[1] + 20, text=event.label)


    def __drawArc(self, arc):
        """ Draw the given arc. """
        start_event = self.__lpo.events[arc.source] # get start event
        end_event = self.__lpo.events[arc.target] # get end event

        intersections = self.__calculateIntersections(start_event, end_event) # calculate intersection points

        # start point of arc
        start = start_event.position[0] + intersections[0][0], start_event.position[1] + intersections[0][1]
        # end point of arc
        end = end_event.position[0] + intersections[1][0], end_event.position[1] + intersections[1][1]
        # create line with arrow head as end
        self.__canvas.create_line(start[0], start[1], end[0], end[1], arrow=LAST, arrowshape=(8.6, 10, 5), width=2)


    def __calculateIntersections(self, start, end):
        """ Calculate intersection point of start and end events with the arc.

        This method calculates two vectors which describe the intersection point of the arc from the
        given start event to the given end event.
        """

        # vector from the center of the start event to the center of the end event
        vector = float(end.position[0] - start.position[0]), float(end.position[1] - start.position[1])
        #calculate a factor to scale the x-component to 10px (half of side length)
        fact = 1
        if vector[0] != 0:
            fact = 10 / math.fabs(vector[0])
        # scale the vector
        start_vector = vector[0] * fact, vector[1] * fact

        # if y-component of vector is larger than 10px or x-component is 0, scale with y-component
        if math.fabs(start_vector[1]) > 10 or vector[0] == 0:
            fact = 10 / math.fabs(vector[1])
            start_vector = vector[0] * fact, vector[1] * fact
        #calculate intersection for arc end
        if vector[0] != 0:
            fact = 10 / math.fabs(vector[0])

        end_vector = -vector[0] * fact, -vector[1] * fact

        if math.fabs(end_vector[1]) > 10 or vector[0] == 0:
            fact = 10 / math.fabs(vector[1])
            end_vector = -vector[0] * fact, -vector[1] * fact

        return start_vector, end_vector


class LpoViewer(Frame):
    """ This class implements the window of the Lpo viewer.

    This class implements a menu and tab management for the LpoView.
    """
    
    def __init__(self, parent):
        """ Create new window. """
        Frame.__init__(self, parent)
        self.__parent = parent
        self.__initUI()

    def __initUI(self):
        """ Set up UI. """
        self.pack(fill=BOTH, expand=1)
        # notebook for LpoView tabs
        self.__notebook = Notebook(self)
        self.__notebook.pack(fill=BOTH, expand=1)
        # menu bar with file menu
        self.__menubar = Menu(self.__parent)
        self.__parent.config(menu=self.__menubar)

        self.__filemenu = Menu(self.__menubar, tearoff=0)
        self.__filemenu.add_command(label="Open", command=self.__onOpen)
        self.__filemenu.add_command(label="Close", command=self.__onClose)
        self.__filemenu.add_command(label="Exit", command=self.__onExit)
        self.__menubar.add_cascade(label="File", menu=self.__filemenu)
        # size and title
        self.__parent.geometry("300x300+300+300")
        self.__parent.title("Lpo viewer Tk")

    def __onExit(self):
        """ Close the app. """
        self.__parent.withdraw()
        self.quit()

    def __onClose(self):
        """ Close the selected LPO. """
        tab = self.__notebook.select()
        if tab != '':
            self.__notebook.forget(tab)
        

    def __onOpen(self):
        """ Open a new LPO (with file chooser). """
        ftypes = [('LPO files', '*.lpo'), ('All files', '*')]
        dialog = filedialog.Open(self, filetypes=ftypes)
        file = dialog.show()

        if file != '':
            self.openLpo(file)

    def openLpo(self, file):
        """ This method shows the LPO contained in the given file as new tab. """
        lpos = partialorder.parse_lpo_file(file) # parse LPO from file
        print(lpos[0])
        self.showLpo(lpos[0]) # show first lpo (Assumption: Only 1 LPO in a file)
    
    def showLpo(self, lpo):
        """ Show the given LPO in a new tab. """
        lpo_view = LpoView(self.__notebook)
        self.__notebook.add(lpo_view, text=lpo.name, sticky="nswe")
        lpo_view.showLpo(lpo)

def main():
    root = Tk()
    app = LpoViewer(root)
    
    if len(sys.argv) > 1: # load LPO if file is given as parameter
        app.openLpo(sys.argv[1])

    if os.path.exists("../abcabc.lpo"): # debug/demo file
        app.openLpo("../abcabc.lpo")
    
    root.mainloop()
    
   

if __name__ == "__main__":
    main()        

