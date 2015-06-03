from pntools import partialorder

def skeleton(lpo):
    minimal = minimal_event_ids(lpo)
    incidence = incidence(lpo)

    for arc in lpo.arcs:
        if arc.source in minimal:
            arc.skeleton = True
        else:
            arc.skeleton = False

    

def preset(lpo, event_id, incidence):
    matrix, events = incidence
    index = events.index(event_id)
    len = len(events)

    preset = set()

    for i in range(0, len):
        matrix[i][event_id] == 1:
            preset.append(events[i])

    return preset



    
    


    
        
def minimal_event_ids(lpo):
    event_ids = set()
    arc_target_ids = set()
    
    for id, event in lpo.events.items():
        event_ids.add(id)

    for arc in lpo.arcs:
        arc_target_ids.add(arc.target)

    return event_ids - arc_target_ids

def incidence(lpo):
    event_ids = tuple(lpos[0].events.keys())

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
    
        
    

lpos = partialorder.parse_lpo_file("../../abcabc.lpo")
lpo = lpos[0]

skeleton(lpo)

for arc in lpo.arcs:
    print(arc.source, " --> ", arc.target, " - ", str(arc.skeleton))









    
