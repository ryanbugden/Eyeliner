# Adds a little eye around points and anchors that are on the
# vertical font dimensions, guidelines, or edges of blue zones.

from mojo.roboFont import version

if version >= "4.0":
    from eyelinerRF4 import *
else:
    from eyelinerRF3 import *