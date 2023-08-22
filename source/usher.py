from mojo.roboFont import version

if version >= "4.4b":  # Syntax change for glyphViewOnCurvePointsSize
    from eyelinerRF4_4 import *
else:
    from eyelinerRF4_2 import *