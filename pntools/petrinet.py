#!/usr/bin/python3
# -*- coding_ utf-8 -*-

""" This program implements a parser and data structure for Petri net files.

This program implements an XML parser and a python data structure for
Petri nets/PNML created with VipTool or MoPeBs.
"""

import sys # argv for test file path
import xml.etree.ElementTree as ET # XML parser
import time # timestamp for id generation
from random import randint # random number for id generation

class PetriNet:
    """ This class represents a Petri net.

    This class represents a Petri net. A Petri net consists of
    a set of labelled labelled transitions, labelled places and
    arcs from places to transitions or transitions to places.

    net.edges: List of all edges of this Petri net
    net.transitions: Map of (id, transition) of all transisions of this Petri net
    net.places: Map of (id, place) of all places of this Petri net
    """
    
    def __init__(self):
        #generate a unique id
        self.id = ("PetriNet" + str(time.time())) + str(randint(0, 1000))
        self.edges = [] # List or arcs
        self.transitions = {} # Map of transitions. Key: transition id, Value: event
        self.places = {} # Map of places. Key: place id, Value: place

    def __str__(self):
        text = '--- Net: ' + self.name + '\nTransitions: '
        for transition in self.transitions.values():
            text += str(transition) + ' '
        text += '\nPlaces: '
        for place in self.places.values():
            text += str(place) + ' '
        text += '\n'
        for edge in self.edges:
                text += str(edge) + '\n'
        text += '---'
        
        return text

class Transition:
    """ This class represents a labelled transition of a Petri net. 

    A transition represents an activity.

    transition.id: Unique ID of this transition.
    transition.label: Label of this transition.

    Layout information:
      transition.position: Position to display the transition in graphical representations.
        Usually a transition is drawn as a square. The position is the center of this square.
      transition.offset: Offest of the transition label.
        Usually the label of a transition is printed centered below the square which
        represents the transition in graphical representations. This offset represents
        a vector which defines a translation of the label inscription from its
        usual position.
    """
    
    def __init__(self):
        self.label = "Transition" # default label of event
        #generate a unique id
        self.id = ("Transition" + str(time.time())) + str(randint(0, 1000))
        self.offset = [0, 0]
        self.position = [0, 0]

    def __str__(self):
        return self.label

class Place:
    """ This class represents a labelled Place of a Petri net. 

    A place represents a resource.

    place.id: Unique ID of this place.
    place.label: Label of this place.
    place.marking: Current marking of this place.
      Usually a marking is the count of tokens contained into this place.

    Layout information:
      place.position: Position to display the place in graphical representations.
        Usually a place is drawn as a circle. The position is the center of this circel.
      place.offset: Offest of the place label.
        Usually the label of a place is printed centered below the circle which
        represents the place in graphical representations. This offset represents
        a vector which defines a translation of the label inscription from its
        usual position.
    """
    
    def __init__(self):
        self.label = "Place" # default label of event
        #generate a unique id
        self.id = ("Place" + str(time.time())) + str(randint(0, 1000))
        self.offset = [0, 0]
        self.position = [0, 0]
        self.marking = 0

    def __str__(self):
        return self.label


class Edge:
    """ This class represents an arc of a Petri net. 

    An edge represents an relation between a place and a transition or a transition
    and a place.

    edge.id: Unique ID of this edge.
    edge.source: ID of the source (start) node of this edge.
    edge.target: ID of the target (end) node of this edge.
    edge.type: ID of the type of this edge.
    edge.inscription: Inscription of this edge.
      The inscription is usually an integer which is interpreted as weight of this edge.
    edge.net: The Petri net which contains this edge.
      This reference is used for the label resolution of the source and target events.
      See __str__ method.
    """
    
    def __init__(self):
        #generate a unique id
        self.id = ("Arc" + str(time.time())) + str(randint(0, 1000))
        self.source = None # id of the source event of this arc
        self.target = None # id of the target event of this arc
        self.type = 'normal' # id of the type of this arc
        self.inscription = "1" # inscription of this arc
        self.net = None # Reference to net object for label resolution of source an target

    def find_source(self):
        if self.source in self.net.transitions:
            return self.net.transitions[self.source]
        else:
            return self.net.places[self.source]

    def find_target(self):
        if self.target in self.net.transitions:
            return self.net.transitions[self.target]
        else:
            return self.net.places[self.target]
        
    def __str__(self):
        return str(self.find_source()) + "-->" + str(self.find_target())


def parse_pnml_file(file):
    """ This method parse all Petri nets of the given file.

    This method expects a path to a VipTool pnml file which
    represent a Petri net (.pnml), parse all Petri nets
    from the file and returns the Petri nets as list of PetriNet
    objects.

    XML format:
    <pnml>
      <net id="...">
        (<page>)
        <name>
          <text>name of Petri net</text>
        </name>
        <transition id="...">
          <name>
            <text>label of transition</text>
            <graphics>
              <offset x="0" y="0"/>
            </graphics>
          </name>
          <graphics>
            <position x="73" y="149"/>
          </graphics>
        </transition>
        ...
        <place id="...">
          <name>
            <text>label of transition</text>
            <graphics>
              <offset x="0" y="0"/>
            </graphics>
          </name>
          <graphics>
            <position x="73" y="149"/>
          </graphics>
          <initialMarking>
            <text>1</text>
          </initialMarking>
        </place>
        ...
        <arc id="..." source="id of source event" target="id of target event">
          <inscription>
            <text>1</text>
          </inscription>
        </arc>
        ...
        (</page>)
      </net>
      ...
    </pnml>
    """
    tree = ET.parse(file) # parse XML with ElementTree
    root = tree.getroot()

    nets = [] # list for parsed PetriNet objects

    for net_node in root.iter('net'):
        # create PetriNet object
        net = PetriNet()
        nets.append(net)
        net.id = net_node.get('id')
        netnmnode = net_node.find('./name/text')
        if netnmnode is not None:
             net.name = netnmnode.text
        else:
             net.name = net.id

        # and parse transitions
        for transition_node in net_node.iter('transition'):
            transition = Transition()
            transition.id = transition_node.get('id')
            trname = transition_node.find('./name/text')
            if trname is not None:
                transition.label = trname.text
	        off_node = transition_node.find('./name/graphics/offset')
	        transition.offset = [int(off_node.get('x')), int(off_node.get('y'))]
            else:
                transition.label = transition.id
	    position_node = transition_node.find('./graphics/position')
            if position_node is not None:
	        transition.position = [int(position_node.get('x')), int(position_node.get('y'))]
            else:
	        transition.position = None

            net.transitions[transition.id] = transition

        # and parse places
        for place_node in net_node.iter('place'):
            place = Place()
            place.id = place_node.get('id')
            placelabnode = place_node.find('./name/text')
            if placelabnode is not None:
                place.label = placelabnode.text
                off_node = place_node.find('./name/graphics/offset')
                place.offset = [int(off_node.get('x')), int(off_node.get('y'))]
            else:
                place.label = place.id
            position_node = place_node.find('./graphics/position')
            if position_node is not None:
                place.position = [int(position_node.get('x')), int(position_node.get('y'))]
            else:
                place.position = None
	    plcmarknode = place_node.find('./initialMarking/text')
            if plcmarknode is not None:
                place.marking = int(plcmarknode.text)
            else:
                place.marking = 0

            net.places[place.id] = place

        # and arcs
        for arc_node in net_node.iter('arc'):
            edge = Edge()
            net.edges.append(edge)

            edge.id = arc_node.get('id')
            edge.source = arc_node.get('source')
            edge.target = arc_node.get('target')
            edge.type = arc_node.get('type')
            if edge.type is None:
                etp = arc_node.find('./type')
                if etp is not None:
                    edge.type = etp.get('value')
                if edge.type is None:
                    edge.type = 'normal'
            inscr_txt = arc_node.find('./inscription/text')
            if inscr_txt is not None:
                edge.inscription = inscr_txt.text
            else:
                edge.inscription = None
            
            edge.net = net
    
    return nets

def write_pnml_file(n, filename, relative_offset=True):
    pnml = ET.Element('pnml')
    net = ET.SubElement(pnml, 'net', id=n.id)
    net_name = ET.SubElement(net, 'name')
    net_name_text = ET.SubElement(net_name, 'text')
    net_name_text.text = n.name

    page = ET.SubElement(net, 'page', id='1')

    for id, t in n.transitions.items():
        transition = ET.SubElement(page, 'transition', id=t.id)
        transition_name = ET.SubElement(transition, 'name')
        transition_name_text = ET.SubElement(transition_name, 'text')
        transition_name_text.text = t.label
        transition_name_graphics = ET.SubElement(transition_name, 'graphics')
        transition_name_graphics_offset = ET.SubElement(transition_name_graphics, 'offset')
        transition_name_graphics_offset.attrib['x'] = str(t.offset[0])
        transition_name_graphics_offset.attrib['y'] = str(t.offset[1])
        transition_graphics = ET.SubElement(transition, 'graphics')
        transition_graphics_position = ET.SubElement(transition_graphics, 'position')
        transition_graphics_position.attrib['x'] = str(t.position[0] if t.position is not None else 0)
        transition_graphics_position.attrib['y'] = str(t.position[1] if t.position is not None else 0)

    for id, p in n.places.items():
        place = ET.SubElement(page, 'place', id=p.id)
        place_name = ET.SubElement(place, 'name')
        place_name_text = ET.SubElement(place_name, 'text')
        place_name_text.text = p.label
        place_name_graphics = ET.SubElement(place_name, 'graphics')
        place_name_graphics_offset = ET.SubElement(place_name_graphics, 'offset')
        place_name_graphics_offset.attrib['x'] = str(p.offset[0] if p.offset is not None else 0)
        place_name_graphics_offset.attrib['y'] = str(p.offset[1] if p.offset is not None else 0)
        place_name_graphics_offset.attrib['x'] = str(p.offset[0] if p.offset is not None else 0)
        place_name_graphics_offset.attrib['y'] = str(p.offset[1] if p.offset is not None else 0)
        place_graphics = ET.SubElement(place, 'graphics')
        place_graphics_position = ET.SubElement(place_graphics, 'position')
        place_graphics_position.attrib['x'] = str(p.position[0] if p.position is not None else 0)
        place_graphics_position.attrib['y'] = str(p.position[1] if p.position is not None else 0)
        place_initialMarking = ET.SubElement(place, 'initialMarking')
        place_initialMarking_text = ET.SubElement(place_initialMarking, 'text')
        place_initialMarking_text.text = str(p.marking)

    for e in n.edges:
        edge = ET.SubElement(page, 'arc', id=e.id, source=e.source, target=e.target, type=e.type)
        edge_inscription = ET.SubElement(edge, 'inscription')
        edge_inscription_text = ET.SubElement(edge_inscription, 'text')
        edge_inscription_text.text = str(e.inscription)

    tree = ET.ElementTree(element=pnml)
    tree.write(filename, encoding="utf-8", xml_declaration=True, method="xml")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        nets = parse_pnml_file(sys.argv[1])
        
        for net in nets:
            print(net)





