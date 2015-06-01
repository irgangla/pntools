#!/usr/bin/python3
# -*- coding_ utf-8 -*-

""" This program implements a viewer for the Petri net data structure.

A Petri net is a graph of transitions and places. Transitions represent
actions and places represent resource containers.

Usage: python petrinet_viewer_tk.py [<pnml-file>]
"""

import math # calculation of intersection point (fabs, ...)
import sys # sys.argv
import petrinet # Petri net parser and data structure
import os # demo file
from tkinter import Tk, Frame, Menu, Canvas, BOTH, LAST, filedialog # UI
from tkinter.ttk import Notebook # Tabs

class PetriNetView(Frame):
    """ This class implements a Petri net widget.

    This class use a canvas to draw a Petri net.
    """

    def __init__(self, parent):
        """ This method creates a new, emtpy PetriNetView. """
        Frame.__init__(self, parent)
        self.__parent = parent
        self.__initUI()
        
        self.__net = None

        self.__node_size = 15

    def __initUI(self):
        """ Set up user interface. """
        self.pack(fill=BOTH, expand=1)
        
        self.__canvas = Canvas(self) # canvas for the Petri net
        self.__canvas.pack(fill=BOTH, expand=1)
        # Scroll with mouse drag gestures
        self.__canvas.bind("<ButtonPress-1>", self.__scroll_start)
        self.__canvas.bind("<B1-Motion>", self.__scroll_move)

    def __scroll_start(self, event):
        """ Scroll Petri net with mouse gestures: Start of scroll event. """
        self.__canvas.scan_mark(event.x, event.y)

    def __scroll_move(self, event):
        """ Scroll Petri net with mouse gestures: Drag event. """
        self.__canvas.scan_dragto(event.x, event.y, gain=1)

        
    def showPetriNet(self, petrinet):
        """ This method show the given LPO in this LpoView. """
        self.__net = petrinet # set Petri net reference
        self.__drawNet() # create Net graph

    def __drawNet(self):
        """ This method draws the Petri net. """
        

        # draw places
        for id, place in self.__net.places.items():
            self.__drawPlace(place)

        # draw transitions
        for id, transition in self.__net.transitions.items():
            self.__drawTransition(transition)

        # draw Petri net edges (arc layer is behind the other layers)
        for edge in self.__net.edges:
            self.__drawEdge(edge)

    def __drawPlace(self, place):
        """ Draw the given place. """
        self.__canvas.create_oval(place.position[0] - self.__node_size, place.position[1] - self.__node_size,
                                  place.position[0] + self.__node_size, place.position[1] + self.__node_size,
                                  outline="#000", fill="#FFFFFF", width=2)
        self.__canvas.create_text(place.position[0], place.position[1] + self.__node_size + 10, text=place.label)

    def __drawTransition(self, transition):
        """ Draw the given place. """
        self.__canvas.create_rectangle(transition.position[0] - self.__node_size, transition.position[1] - self.__node_size,
                                       transition.position[0] + self.__node_size, transition.position[1] + self.__node_size,
                                       outline="#000", fill="#FFFFFF", width=2)
        self.__canvas.create_text(transition.position[0], transition.position[1] + self.__node_size + 10, text=transition.label)


    def __drawEdge(self, edge):
        """ Draw the given edge. """
        start_node = edge.find_source() # get start event
        end_node = edge.find_target() # get end event

        intersections = self.__calculateIntersections(start_node, end_node) # calculate intersection points

        # start point of arc
        start = start_node.position[0] + intersections[0][0], start_node.position[1] + intersections[0][1]
        # end point of arc
        end = end_node.position[0] + intersections[1][0], end_node.position[1] + intersections[1][1]
        # create line with arrow head as end
        self.__canvas.create_line(start[0], start[1], end[0], end[1], arrow=LAST, arrowshape=(8.6, 10, 5), width=2)


    def __calculateIntersections(self, start, end):
        """ Calculate intersection point of start and end events with the arc.

        This method calculates two vectors which describe the intersection point of the arc from the
        given start event to the given end event.
        """

        # vector from the center of the start event to the center of the end event
        vector = float(end.position[0] - start.position[0]), float(end.position[1] - start.position[1])
        
        if type(start) is petrinet.Transition:
            #calculate a factor to scale the x-component to 10px (half of side length)
            fact = 1
            if vector[0] != 0:
                fact = self.__node_size / math.fabs(vector[0])
            # scale the vector
            start_vector = vector[0] * fact, vector[1] * fact

            # if y-component of vector is larger than 10px or x-component is 0, scale with y-component
            if math.fabs(start_vector[1]) > self.__node_size or vector[0] == 0:
                fact = self.__node_size / math.fabs(vector[1])
                start_vector = vector[0] * fact, vector[1] * fact
        else:
            fact = self.__node_size / math.sqrt(vector[0] ** 2 + vector[1] ** 2)
            start_vector = vector[0] * fact, vector[1] * fact
            
        #calculate intersection for arc end
        if type(end) is petrinet.Transition:
            if vector[0] != 0:
                fact = self.__node_size / math.fabs(vector[0])

            end_vector = -vector[0] * fact, -vector[1] * fact

            if math.fabs(end_vector[1]) > self.__node_size or vector[0] == 0:
                fact = self.__node_size / math.fabs(vector[1])
                end_vector = -vector[0] * fact, -vector[1] * fact
        else:
            fact = self.__node_size / math.sqrt(vector[0] ** 2 + vector[1] ** 2)
            end_vector = -vector[0] * fact, -vector[1] * fact

        return start_vector, end_vector


class PetriNetViewer(Frame):
    """ This class implements the window of the Petri net viewer.

    This class implements a menu and tab management for the PetriNetView.
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
        self.__parent.title("Petri net viewer Tk")

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
        """ Open a new PNML file (with file chooser). """
        ftypes = [('Petri net files', '*.pnml'), ('All files', '*')]
        dialog = filedialog.Open(self, filetypes=ftypes)
        file = dialog.show()

        if file != '':
            self.openPetriNet(file)

    def openPetriNet(self, file):
        """ This method shows the Petri net contained in the given file as new tab. """
        nets = petrinet.parse_pnml_file(file) # parse Petri net from file
        print(nets[0])
        self.showPetriNet(nets[0]) # show first Petri net (Assumption: Only 1 net in a file)
    
    def showPetriNet(self, net):
        """ Show the given Petri net in a new tab. """
        net_view = PetriNetView(self.__notebook)
        self.__notebook.add(net_view, text=net.name, sticky="nswe")
        net_view.showPetriNet(net)

def main():
    root = Tk()
    app = PetriNetViewer(root)
    
    if len(sys.argv) > 1: # load LPO if file is given as parameter
        app.openPetriNet(sys.argv[1])

    if os.path.exists("../example.pnml"): # debug/demo file
        app.openPetriNet("../example.pnml")
    
    root.mainloop()
    
   

if __name__ == "__main__":
    main()        

