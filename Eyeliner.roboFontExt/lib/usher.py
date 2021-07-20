# Adds a little eye around points and anchors that are on the
# vertical font dimensions, guidelines, or edges of blue zones.

# Ryan Bugden
# v2.0.2 : 2021.07.20
# v2.0.1 : 2021.07.02
# v1.2.9 : 2021.03.17
# v1.2.8 : 2021.01.30
# v1.2.7 : 2020.09.14
# v1.2.5 : 2020.07.15
# v1.2.1 : 2020.04.03
# v1.2.0 : 2020.03.26
# v1.1.1 : 2020.01.27
# v1.0.0 : 2020.01.24
# v0.9.0 : 2019.06.04

from mojo.roboFont import version

if version >= "4.0":
    from eyelinerRF4 import *
else:
    from eyelinerRF3 import *

Eyeliner()