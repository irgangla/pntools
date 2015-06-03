from pntools import partialorder
from pntools.partialorder import LPO, Event, Arc

def transitive_closure(lpo):
    incidence = incidence_matrix(lpo)
    minimal = minimal_event_ids(lpo)

    for event_id in minimal:
        recursive_add_transitive_arcs(incidence, event_id)

    matrix, event_ids = incidence

    invalid_arcs = []
    
    for arc in lpo.arcs:
        source = event_ids.index(arc.source)
        target = event_ids.index(arc.target)
        if matrix[source][target] == 0:
            invalid_arcs.append(arc)
        elif matrix[source][target] == 1:
            matrix[source][target] = 0

    for arc in invalid_arcs:
        lpo.arcs.remove(arc)

    for i in range(0, len(event_ids)):
        for j in range(0, len(event_ids)):
            if matrix[i][j] == 1:
                arc = Arc()
                arc.lpo = lpo
                arc.source = event_ids[i]
                arc.target = event_ids[j]
                arc.user_drawn = False
                lpo.arcs.append(arc)

def recursive_add_transitive_arcs(incidence, event_id):
    pre_ids = preset(incidence, event_id)
    post_ids = postset(incidence, event_id)

    matrix, event_ids = incidence

    for pre_id in pre_ids:
        for post_id in post_ids:
            matrix[event_ids.index(pre_id)][event_ids.index(post_id)] = 1

    for post_id in post_ids:
        recursive_add_transitive_arcs(incidence, post_id)
    
    
def minimal_event_ids(lpo):
    event_ids = set()
    arc_target_ids = set()
    
    for id, event in lpo.events.items():
        event_ids.add(id)

    for arc in lpo.arcs:
        arc_target_ids.add(arc.target)

    return event_ids - arc_target_ids
        
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

def preset(incidence, event_id):
    preset = set()
    
    matrix, events = incidence
    index = events.index(event_id)
    
    for i in range(0, len(events)):
        if matrix[i][index] == 1:
            preset.add(events[i])

    return preset

def postset(incidence, event_id):
    postset = set()
    
    matrix, events = incidence
    index = events.index(event_id)
    
    for i in range(0, len(events)):
        if matrix[index][i] == 1:
            postset.add(events[i])

    return postset

lpo = LPO()

a = Event()
a.label = "a"
lpo.events[a.id] = a
b = Event()
b.label = "b"
lpo.events[b.id] = b
c = Event()
c.label = "c"
lpo.events[c.id] = c
d = Event()
d.label = "d"
lpo.events[d.id] = d

arc = Arc()
arc.user_drawn = True
arc.lpo = lpo
arc.source = a.id
arc.target = b.id
lpo.arcs.append(arc)

arc = Arc()
arc.user_drawn = True
arc.lpo = lpo
arc.source = b.id
arc.target = c.id
lpo.arcs.append(arc)

arc = Arc()
arc.user_drawn = True
arc.lpo = lpo
arc.source = d.id
arc.target = c.id
lpo.arcs.append(arc)

arc = Arc()
arc.user_drawn = False
arc.lpo = lpo
arc.source = a.id
arc.target = d.id
lpo.arcs.append(arc)

transitive_closure(lpo)

for arc in lpo.arcs:
    print(arc, " - ", str(arc.user_drawn))






