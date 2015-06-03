from pntools import partialorder, partialorder_renderer
from pntools.algorithm import lpo_skeleton, lpo_transitive

lpos = partialorder.parse_lpo_file("abcabc.lpo")
lpo = lpos[0]

lpo_skeleton.skeleton(lpo)
lpo_transitive.transitive_closure(lpo)

image = partialorder_renderer.draw_lpo(lpo, skeleton=True, transitive=True)
image.show()
