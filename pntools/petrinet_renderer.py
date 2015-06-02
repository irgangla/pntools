#!/usr/bin/python3
# -*- coding_ utf-8 -*-

""" This program implements a renderer for Petri net files. """

from PIL import Image, ImageDraw, ImageFont, ImageFilter # Python image library (Pillow)
import petrinet # Petri net data structure
import math
import sys
import os

def calculate_size(petrinet):
    """ This function calculates the size and minimum coordinate
    of the Petri net.

    return: ((width, height), (min_x, min_y))
    """
    
    minmax = [0, 0, 0, 0]
    for id, transition in petrinet.transitions.items():
        x, y = transition.position
        if x < minmax[0]:
            minmax[0] = x
        if x > minmax[2]:
            minmax[2] = x
        if y < minmax[1]:
            minmax[1] = y
        if y > minmax[3]:
            minmax[3] = y

    for id, place in petrinet.places.items():
        x, y = place.position
        if x < minmax[0]:
            minmax[0] = x
        if x > minmax[2]:
            minmax[2] = x
        if y < minmax[1]:
            minmax[1] = y
        if y > minmax[3]:
            minmax[3] = y

    width = minmax[2] - minmax[0] + 100
    height = minmax[3] - minmax[1] + 100

    offx = minmax[0]
    if offx != 0:
        offx - 50;
    offy = minmax[1]
    if offy != 0:
        offy - 50;
    
    
    return ((width, height), (offx, offy))

def create_image(size):
    """ This function creates a new image with RGB color space,
    white background color and the given size.

    size: Size of the image.
    return: new Image
    """
    
    return Image.new('RGB', size, color=(255,255,255))

def draw_transition(transition, draw, doffset):
    """ Helper method for transition drawing. """
    scale = 4
    x, y = transition.position
    x = (x + doffset[0]) * scale
    y = (y + doffset[1]) * scale
    halfside = 16 * scale
    linewidth = 2 * scale
    distance = 2 * scale
    offset = transition.offset[0] * scale, transition.offset[1] * scale
    

    font = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 12 * scale)

    draw.rectangle([x - halfside, y - halfside, x + halfside, y + halfside],
                   fill=(0, 0, 0), outline=(0, 0, 0))
    draw.rectangle([x - halfside + linewidth, y - halfside + linewidth,
                    x + halfside - linewidth, y + halfside - linewidth],
                   fill=(255, 255, 255), outline=(255, 255, 255))
    fontsize = font.getsize(transition.label)
    draw.text((x - fontsize[0] / 2 + offset[0], y + halfside + distance + offset[1]),
              transition.label, font=font, fill=(0, 0, 0))

def draw_place(place, draw, doffset):
    """ Helper method for place drawing. """
    scale = 4
    x, y = place.position
    x = (x + doffset[0]) * scale
    y = (y + doffset[1]) * scale
    halfside = 16 * scale
    linewidth = 2 * scale
    marksize = 3 * scale
    distance = 2 * scale
    offset = place.offset[0] * scale, place.offset[1] * scale

    font = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 12 * scale)

    draw.ellipse([x - halfside, y - halfside, x + halfside, y + halfside],
                   fill=(0, 0, 0), outline=(0, 0, 0))
    draw.ellipse([x - halfside + linewidth, y - halfside + linewidth,
                    x + halfside - linewidth, y + halfside - linewidth],
                   fill=(255, 255, 255), outline=(255, 255, 255))
    
    fontsize = font.getsize(place.label)
    draw.text((x - fontsize[0] / 2 + offset[0], y + halfside + distance + offset[1]),
              place.label, font=font, fill=(0, 0, 0))

    if place.marking == 0:
        pass
    elif place.marking == 1:
        draw.ellipse([x - marksize, y - marksize, x + marksize, y + marksize],
                     fill=(0, 0, 0), outline=(0, 0, 0))
    elif place.marking == 2:
        markoff = -halfside / 3
        draw.ellipse([x - marksize + markoff, y - marksize + markoff,
                      x + marksize + markoff, y + marksize + markoff],
                     fill=(0, 0, 0), outline=(0, 0, 0))
        markoff = halfside / 3
        draw.ellipse([x - marksize + markoff, y - marksize + markoff,
                      x + marksize + markoff, y + marksize + markoff],
                     fill=(0, 0, 0), outline=(0, 0, 0))
    else:
       fontsize = font.getsize(str(place.marking))
       draw.text((x - fontsize[0] / 2, y - fonzsize[1] / 2), str(place.marking),
                 font=font, fill=(0, 0, 0)) 
        
        

def draw_edge(edge, draw, doffset):
    """ Helper method for edge drawing. """
    scale = 4
    width = 2 * scale
    tipsize = 10 * scale
    
    halfside = 16

    start_node = edge.find_source() # get start event
    end_node = edge.find_target() # get end event

    intersections = calculate_intersections(start_node, end_node, halfside) # calculate intersection points

    # start point of arc
    start = start_node.position[0] + intersections[0][0], start_node.position[1] + intersections[0][1]
    # end point of arc
    end = end_node.position[0] + intersections[1][0], end_node.position[1] + intersections[1][1]

    vector = (float(start_node.position[0] - end_node.position[0]),
              float(start_node.position[1] - end_node.position[1]))
    vector_length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    tipcenter = (vector[0] * (tipsize / 2) / vector_length,
                 vector[1] * (tipsize / 2) / vector_length)

    start = (start[0] + doffset[0]) * scale, (start[1] + doffset[1]) * scale
    end = (end[0] + doffset[0]) * scale, (end[1] + doffset[1]) * scale

    draw.line([start[0], start[1], end[0] + tipcenter[0], end[1] + tipcenter[1]],
              fill=(0, 0, 0), width=width)

    tip = calculate_tip(start_node, end_node, tipsize)

    draw.polygon([end, (end[0] + tip[0][0], end[1] + tip[0][1]),
                  (end[0] + tip[1][0], end[1] + tip[1][1])], outline=(0, 0, 0), fill=(0, 0, 0))
    

def calculate_tip(start, end, tipsize):
    """ Helper function for tip point calculation.

    return ((vektor1_x, vektor1_y), (vektor2_x, vektor2_y))
    """
    vector = float(start.position[0] - end.position[0]), float(start.position[1] - end.position[1])
    vector_length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    
    vector_sized = vector[0] * tipsize / vector_length, vector[1] * tipsize / vector_length

    alpha = 30 * 2 * math.pi / 360

    sin_alpha = math.sin(alpha)
    cos_alpha = math.cos(alpha)

    tip1 = (vector_sized[0] * cos_alpha - vector_sized[1] * sin_alpha,
            vector_sized[0] * sin_alpha + vector_sized[1] * cos_alpha)

    sin_alpha = math.sin(-alpha)
    cos_alpha = math.cos(-alpha)

    tip2 = (vector_sized[0] * cos_alpha - vector_sized[1] * sin_alpha,
            vector_sized[0] * sin_alpha + vector_sized[1] * cos_alpha)

    return tip1, tip2


def calculate_intersections(start, end, halfside):
    """ Helper function for edge intersection point calculation. """
    # vector from the center of the start event to the center of the end event
    vector = float(end.position[0] - start.position[0]), float(end.position[1] - start.position[1])
        
    if type(start) is petrinet.Transition:
        start_vector = calculate_intersection_transition(vector, halfside)
    else:
        start_vector = calculate_intersection_place(vector, halfside)
            
    #calculate intersection for arc end
    if type(end) is petrinet.Transition:
        end_vector = calculate_intersection_transition((-vector[0], -vector[1]), halfside)
    else:
        end_vector = calculate_intersection_place((-vector[0], -vector[1]), halfside)

    return start_vector, end_vector

def calculate_intersection_transition(vector, halfside):
    """ Helper function, calculates intersection of edge and transition. """
    #calculate a factor to scale the x-component to 10px (half of side length)
    fact = 1
    if vector[0] != 0:
        fact = halfside / math.fabs(vector[0])

    # scale the vector
    intersection_vector = vector[0] * fact, vector[1] * fact

    # if y-component of vector is larger than halfside or
    # x-component is 0, scale with y-component
    if math.fabs(intersection_vector[1]) > halfside or vector[0] == 0:
        fact = halfside / math.fabs(vector[1])
        intersection_vector = vector[0] * fact, vector[1] * fact

    return intersection_vector[0], intersection_vector[1]

def calculate_intersection_place(vector, halfside):
    """ Helper function, calculates intersection of edge and place. """
    fact = halfside / math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    intersection_vector = vector[0] * fact, vector[1] * fact

    return intersection_vector[0], intersection_vector[1]

def draw_net(petrinet):
    """ This method renders the given Petri net as an Image object. """
    size, off = calculate_size(petrinet)
    doffset = -off[0], -off[1]
    w, h = size
    image = create_image((w * 4, h * 4))
    d = ImageDraw.Draw(image)

    for id, transition in petrinet.transitions.items():
        draw_transition(transition, d, doffset)

    for id, place in petrinet.places.items():
        draw_place(place, d, doffset)

    for edge in petrinet.edges:
        draw_edge(edge, d, doffset)
    
    return image

def antialias(image, factor):
    """ This method applies an anti alias filter to the given image. Therefore
    the image size is reduced by the given factor.
    """
    x, y = image.size
    img = image.resize((int(x / factor), int(y / factor)), Image.ANTIALIAS)
    
    return img
    
if __name__ == "__main__":
    if len(sys.argv) > 1: # load Petri net if file is given as parameter
        nets = petrinet.parse_pnml_file(sys.argv[1])
        i = 1
        for net in nets:
            img = draw_net(net)
            img = antialias(img, 2)
            img.show()
            img.save("petri-net-%d.png" % i)
            i += 1
            
        

    if os.path.exists("../example.pnml"): # debug/demo file
        nets = petrinet.parse_pnml_file("../example.pnml")
        img = draw_net(nets[0])
        img = antialias(img, 2)
        img.show()
        img.save("../example.png")


