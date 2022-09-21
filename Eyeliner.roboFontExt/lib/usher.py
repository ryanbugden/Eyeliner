# Adds a little eye around points and anchors that are on the
# vertical font dimensions, guidelines, or edges of blue zones.

from mojo.roboFont import version

if version >= "4.0":
    if version >= "4.2":
        from eyelinerRF4_2 import *
    else:
        from eyelinerRF4 import *
else:
    from eyelinerRF3 import *