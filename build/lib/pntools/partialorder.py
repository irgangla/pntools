#!/usr/bin/python3
# -*- coding_ utf-8 -*-

""" This program implements a parser and data structure for LPO files.

This program implements an XML parser and a python data structure for
labelled partial order files created with VipTool or MoPeBs.
"""

import sys # argv for test file path
import xml.etree.ElementTree as ET # XML parser
import time # timestamp for id generation
from random import randint # random number for id generation

class LPO:
    """ This class represents a LPO.

    This class represents a labelled partial order. A labelled
    partial order consists of a set of labelled events which
    are partially ordered.

    lpo.arcs: List of all arcs of this LPO
    lpo.events: Map of (id, event) of all events of this LPO
    """
    
    def __init__(self):
        self.arcs = [] # List or arcs (arcs order events)
        self.events = {} # Map of events. Key: event id, Value: event

    def __str__(self):
        text = '--- LPO: ' + self.name + '\n'
        for event in self.events.values():
            text += str(event) + ' '
        text += '\n'
        for arc in self.arcs:
            if arc.user_drawn:
                text += str(arc) + '\n'
        text += '---'
        
        return text

class Event:
    """ This class represents a labelled event of a LPO. 

    An event represents a occurence of an activity and is labeled
    with this actitvty.

    event.id: Unique ID of this event.
    event.label: Label of this event.

    Layout information:
      event.position: Position to display the event in graphical representations.
        Usually an event is drawn as a filled square. The position is the center
        of this square.
      event.offset: Offest of the event label.
        Usually the label of an event is printed centered below the square which
        represents the event in graphical representations. This offset represents
        a vector which defines a translation of the label inscription from its
        usual position.
    """
    
    def __init__(self):
        self.label = "Event" # default label of event
        #generate a unique id
        self.id = ("Event" + str(time.time())) + str(randint(0, 1000))
        self.offset = [0, 0]
        self.position = [0, 0]

    def __str__(self):
        return self.label + "@(" + str(self.position[0]) + ", " + str(self.position[1]) + ")"

class Arc:
    """ This class represents an arc of a LPO. 

    An arc represents an order between two events.

    arc.id: Unique ID of this arc.
    arc.source: ID of the source (start) event of this arc.
      The source event of an arc have to occur before the end event of an arc.
    arc.target: ID of the target (end) event of this arc.
      The target event of an arc have to occur after the source event of an arc.
    arc.user_drawn: This flag shows is this arc is user defined or calculated.
      The user_drawn arcs are used to calculate the transitive closure of a LPO and
      its skeleton.
    arc.lpo: The LPO which contains this arc.
      This reference is used for the label resolution of the source and target events.
      See __str__ method.
    """
    
    def __init__(self):
        #generate a unique id
        self.id = ("Arc" + str(time.time())) + str(randint(0, 1000))
        self.source = None # id of the source event of this arc
        self.target = None # id of the target event of this arc
        self.user_drawn = False # True if the edge was defined from the user
        self.lpo = None # Reference to LPO object for label resolution of source an target

    def __str__(self):
        return str(self.lpo.events[self.source]) + " --> " + str(self.lpo.events[self.target])
    


def parse_lpo_file(file):
    """ This method parse all LPOs of the given file.

    This method expects a path to a VipTool XML file which
    represent a labelled partial order (LPO), parse all LPOs
    from the file and returns the LPOs as list of LPO objects.

    XML format:
    <pnml>
      <lpo id="...">
        <name>
          <value>name of lpo</value>
        </name>
        <event id="...">
          <name>
            <value>label of event</value>
            <graphics>
              <offset x="0" y="0"/>
            </graphics>
          </name>
          <graphics>
            <position x="73" y="149"/>
          </graphics>
        </event>
        ...
        <lpoArc id="..." source="id of source event" target="id of target event">
          <graphics userDrawn="true"/>
        </lpoArc>
        ...
      </lpo>
      ...
    </pnml>
    """
    tree = ET.parse(file) # parse XML with ElementTree
    root = tree.getroot()

    lpos = [] # list for parsed LPO objects

    for lpo_node in root.iter('lpo'):
        # create LPO object
        lpo = LPO()
        lpos.append(lpo)
        lpo.name = lpo_node.find('./name/value').text

        # and parse events
        for event_node in lpo_node.iter('event'):
            event = Event()
            event.id = event_node.get('id')
            event.label = event_node.find('./name/value').text
            off_node = event_node.find('./name/graphics/offset')
            event.offset = [int(off_node.get('x')), int(off_node.get('y'))]
            position_node = event_node.find('./graphics/position')
            event.position[0] = int(position_node.get('x'))
            event.position[1] = int(position_node.get('y'))

            lpo.events[event.id] = event

        # and arcs
        for arc_node in lpo_node.iter('lpoArc'):
            arc = Arc()
            lpo.arcs.append(arc)

            arc.id = arc_node.get('id')
            arc.source = arc_node.get('source')
            arc.target = arc_node.get('target')
            # user drawn means the user defined this arc
            arc.user_drawn = bool(arc_node.find('graphics').get('userDrawn') == "true")

            arc.lpo = lpo
    
    return lpos


if __name__ == "__main__":
    lpos = parse_lpo_file(sys.argv[1])
    
    for lpo in lpos:
        print(lpo)


