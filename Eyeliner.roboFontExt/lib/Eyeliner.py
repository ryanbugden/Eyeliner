import mojo.drawingTools as db

from fontTools.misc.fixedTools import otRound
from lib.tools.defaults import getDefaultColor, getDefault
from lib.tools.misc import NSColorToRgba
from mojo.events import addObserver
from mojo.UI import getGlyphViewDisplaySettings

rad_base = getDefault("glyphViewOncurvePointsSize") * 1.75

class Eyeliner():

    '''
    Adds a little eye around points and anchors that are on the
    vertical font dimensions or guidelines.

    Ryan Bugden
    v1.2.7 : 2020.09.14
    v1.2.5 : 2020.07.15
    v1.2.1 : 2020.04.03
    v1.2.0 : 2020.03.26
    v1.1.1 : 2020.01.27
    v1.0.0 : 2020.01.24
    v0.9.0 : 2019.06.04
    '''

    def __init__(self):

        self.col_font_dim = self.getFlattenedAlpha(
            NSColorToRgba(getDefaultColor("glyphViewMetricsColor")))
        self.col_glob_guides = self.getFlattenedAlpha(
            NSColorToRgba(getDefaultColor("glyphViewGlobalGuidesColor")))
        self.col_loc_guides = self.getFlattenedAlpha(
            NSColorToRgba(getDefaultColor("glyphViewLocalGuidesColor")))

        r, g, b, a = NSColorToRgba(
            getDefaultColor("glyphViewBluesColor"))
        self.col_blues = (r, g, b, 1)
        r, g, b, a = NSColorToRgba(
            getDefaultColor("glyphViewFamilyBluesColor"))
        self.col_fBlues = (r, g, b, 1)

        self.scale = 0
        self.radius = 0

        addObserver(self, "drawBackground", "drawBackground")
        addObserver(self, "drawBackground", "drawBackgroundInactive")

    def getFlattenedAlpha(self, color):

        # flatten transparency of eye, using background color preference
        r, g, b, a = color
        r2, g2, b2, a2 = NSColorToRgba(
            getDefaultColor("glyphViewBackgroundColor"))
        r3 = r2 + (r - r2) * a
        g3 = g2 + (g - g2) * a
        b3 = b2 + (b - b2) * a

        return (r3, g3, b3, 1)

    def drawBackground(self, notification):

        self.g = notification["glyph"]
        self.f = self.g.font

        self.scale = notification['scale']
        self.radius = rad_base * self.scale

        if self.g is not None:
            # on-curve points
            for c in self.g:
                for pt in c.points:
                    if pt.type != 'offcurve':
                        self.checkMetrics(pt.x, pt.y)
            # anchors
            for a in self.g.anchors:
                self.checkMetrics(a.x, a.y)

    def checkMetrics(self, x, y):

        # get font dimensions y's
        font_dim = [
            self.f.info.descender, 0, self.f.info.xHeight,
            self.f.info.ascender, self.f.info.capHeight]
        # get guide x's and y's
        f_guide_xs = {}
        f_guide_ys = {}
        for guideline in self.f.guidelines:
            if guideline.angle in [0, 180]:
                f_guide_ys[otRound(guideline.y)] = guideline.color
            elif guideline.angle in [90, 270]:
                f_guide_xs[otRound(guideline.x)] = guideline.color
        # get blue y's and whether they're set to be displayed
        blue_vals = self.f.info.postscriptBlueValues + self.f.info.postscriptOtherBlues
        fBlue_vals = self.f.info.postscriptFamilyBlues + self.f.info.postscriptFamilyOtherBlues
        blues_on = getGlyphViewDisplaySettings()['Blues']
        try:
            fBlues_on = getGlyphViewDisplaySettings()['Family Blues']
        except KeyError:  # RF 4
            fBlues_on = getGlyphViewDisplaySettings()['FamilyBlues']

        if self.g is not None:

            g_guide_xs = {}
            g_guide_ys = {}
            for guideline in self.g.guidelines:
                if guideline.angle in [0, 180]:
                    g_guide_ys[otRound(guideline.y)] = guideline.color
                elif guideline.angle in [90, 270]:
                    g_guide_xs[otRound(guideline.x)] = guideline.color

            angle = 0
            color = None

            # ==== HORIZONTAL STUFF ==== #
            # global horizontal guides
            if otRound(y) in f_guide_ys.keys():
                color = f_guide_ys[otRound(y)]
                if color is None:
                    color = self.col_glob_guides
                self.drawEye(x, y, color, angle)

            # local horizontal guides
            elif otRound(y) in g_guide_ys.keys():
                color = g_guide_ys[otRound(y)]
                if color is None:
                    color = self.col_loc_guides
                self.drawEye(x, y, color, angle)

            # font dimensions
            elif otRound(y) in font_dim:
                color = self.col_font_dim
                self.drawEye(x, y, color, angle)

            # blues
            elif otRound(y) in blue_vals:
                if blues_on is True:
                    color = self.col_blues
                    self.drawEye(x, y, color, angle)

            # family blues
            elif otRound(y) in fBlue_vals:
                if fBlues_on is True:
                    color = self.col_fBlues
                    self.drawEye(x, y, color, angle)

            # ==== VERTICAL STUFF ==== #
            angle = 90

            # global vertical guides
            if otRound(x) in f_guide_xs.keys():
                color = f_guide_xs[otRound(x)]
                if color is None:
                    color = self.col_glob_guides
                self.drawEye(x, y, color, angle)

            # local vertical guides
            elif otRound(x) in g_guide_xs.keys():
                color = g_guide_xs[otRound(x)]
                if color is None:
                    color = self.col_loc_guides
                self.drawEye(x, y, color, angle)

    def drawEye(self, x, y, color, angle):

        stretch = 0.7
        db.save()
        # rounding the eye to nearest unit even though point might not be:
        db.translate(otRound(x), otRound(y))
        db.rotate(angle)

        db.fill(None)
        db.strokeWidth(self.scale / 2)
        db.stroke(*color)

        db.newPath()
        db.moveTo(
            (6 * self.radius * stretch, 0))
        db.curveTo(
            (2 * self.radius * stretch, 0),
            (1.25 * self.radius * stretch, -self.radius),
            (0, -self.radius))
        db.curveTo(
            (-1.25 * self.radius * stretch, -self.radius),
            (-2 * self.radius, 0),
            (-6 * self.radius * stretch, 0))
        db.curveTo(
            (-2 * self.radius * stretch, 0),
            (-1.25 * self.radius * stretch, self.radius),
            (0, self.radius))
        db.curveTo(
            (1.25 * self.radius * stretch, self.radius),
            (2 * self.radius * stretch, 0),
            (6 * self.radius * stretch, 0))
        db.drawPath()
        db.closePath()
        db.restore()


Eyeliner()
