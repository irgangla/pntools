from pntools import partialorder

def skeleton(lpo):
    incidence = incidence_matrix(lpo)

    for arc in lpo.arcs:
        if is_a_skeleton_arc(incidence, arc):
            arc.skeleton = True
        else:
            arc.skeleton = False

def is_a_skeleton_arc(incidence, arc):
    matrix, events = incidence
    source = events.index(arc.source)
    target = events.index(arc.target)

    for i in range(0, len(events)):
        if i != source and matrix[i][target] == 1:
            if is_path_to(incidence, source, i):
                return False

    return True

def is_path_to(incidence, index_to_find, index_to_start):
    matrix, events = incidence
    
    for i in range(0, len(events)):
        if matrix[i][index_to_start] == 1:
            if i == index_to_find:
                return True

    for i in range(0, len(events)):
        if matrix[i][index_to_start] == 1:
            if is_path_to(incidence, index_to_find, i):
                return True

    return False

    
def incidence_matrix(lpo):
    event_ids = tuple(lpo.events.keys())

    incidence = []
    for id in event_ids:
        line = []
        for id in event_ids:
            line.append(0)
        incidence.append(line)

    for arc in lpo.arcs:
        if arc.user_drawn:
            source = event_ids.index(arc.source)
            target = event_ids.index(arc.target)
            incidence[source][target] = 1

    return incidence, event_ids











    
