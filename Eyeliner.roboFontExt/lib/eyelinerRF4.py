from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber
from mojo.UI import CurrentGlyphWindow

from mojo.UI import getGlyphViewDisplaySettings
from lib.tools.defaults import getDefaultColor, getDefault
from fontTools.misc.fixedTools import otRound
from lib.tools.misc import NSColorToRgba


class Eyeliner(Subscriber):

    def build(self):
        
        try:
            self.g = CurrentGlyph()
        except:
            self.g = None
            
        try:
            self.scale = CurrentGlyphWindow().getGlyphView().scale()
        except:
            self.scale = 1
            
        self.bgContainer = self.getGlyphEditor().extensionContainer(
            identifier="com.roboFont.Eyeliner.background", 
            location="background", 
            clear=True
            )

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
        
        self.beginDrawing()
        
    def destroy(self):
        self.bgContainer.clearSublayers()

    def getFlattenedAlpha(self, color):
        # flatten transparency of eye, using background color preference
        r, g, b, a = color
        r2, g2, b2, a2 = NSColorToRgba(
            getDefaultColor("glyphViewBackgroundColor"))
        r3 = r2 + (r - r2) * a
        g3 = g2 + (g - g2) * a
        b3 = b2 + (b - b2) * a

        return (r3, g3, b3, 1)

    def glyphEditorGlyphDidChange(self, info):
        self.g = info["glyph"]
        self.beginDrawing()
        
    def glyphEditorDidMouseDrag(self, info):
        self.g = info["glyph"]
        self.beginDrawing()
        
    def glyphEditorDidSetGlyph(self, info):
        self.g = info["glyph"]
        self.beginDrawing()            
            
    def glyphEditorWillScale(self, info):
        self.scale = info["scale"]
        self.beginDrawing()
        
    def beginDrawing(self):
        if self.g == None:
            return
        self.f = self.g.font
            
        self.bgContainer.clearSublayers()
        self.radius = (getDefault("glyphViewOncurvePointsSize") * 1.75) / self.scale

        onCurves_on = getGlyphViewDisplaySettings()['OnCurvePoints']
        anchors_on = getGlyphViewDisplaySettings()['Anchors']
        
        # on-curve points
        if onCurves_on is True:
            for c in self.g:
                for pt in c.points:
                    if pt.type != 'offcurve':
                        self.checkMetrics(pt.x, pt.y)
        # anchors
        if anchors_on is True:
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
        pathLayer = self.bgContainer.appendPathSublayer(
            strokeColor=color,
            fillColor=None,
            strokeWidth=1
            )
            
        pen = pathLayer.getPen()
        stretch = 0.7
        
        if angle == 0 or angle == 180:
            pen.moveTo(
                (x + 6 * self.radius * stretch, y + 0))
            pen.curveTo(
                (x + 2 * self.radius * stretch, y + 0),
                (x + 1.25 * self.radius * stretch, y + -self.radius),
                (x + 0, y + -self.radius))
            pen.curveTo(
                (x + -1.25 * self.radius * stretch, y + -self.radius),
                (x + -2 * self.radius, y + 0),
                (x + -6 * self.radius * stretch, y + 0))
            pen.curveTo(
                (x + -2 * self.radius * stretch, y + 0),
                (x + -1.25 * self.radius * stretch, y + self.radius),
                (x + 0, y + self.radius))
            pen.curveTo(
                (x + 1.25 * self.radius * stretch, y + self.radius),
                (x + 2 * self.radius * stretch, y + 0),
                (x + 6 * self.radius * stretch, y + 0))
            pen.closePath()
        else:
            pen.moveTo(
                (x + 0, y + 6 * self.radius * stretch))
            pen.curveTo(
                (x + 0, y + 2 * self.radius * stretch),
                (x + -self.radius, y + 1.25 * self.radius * stretch),
                (x + -self.radius, y + 0))
            pen.curveTo(
                (x + -self.radius, y + -1.25 * self.radius * stretch),
                (x + 0, y + -2 * self.radius),
                (x + 0, y + -6 * self.radius * stretch))
            pen.curveTo(
                (x + 0, y + -2 * self.radius * stretch),
                (x + self.radius, y + -1.25 * self.radius * stretch),
                (x + self.radius, y + 0))
            pen.curveTo(
                (x + self.radius, y + 1.25 * self.radius * stretch),
                (x + 0, y + 2 * self.radius * stretch),
                (x + 0, y + 6 * self.radius * stretch))
            pen.closePath()
        
        
registerGlyphEditorSubscriber(Eyeliner)
