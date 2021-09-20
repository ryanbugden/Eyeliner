from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber
from mojo.UI import CurrentGlyphWindow

from mojo.UI import getGlyphViewDisplaySettings
from lib.tools.defaults import getDefaultColor, getDefault
from fontTools.misc.fixedTools import otRound
from lib.tools.misc import NSColorToRgba

import merz
from merz.tools.drawingTools import NSImageDrawingTools


rad_base = getDefault("glyphViewOncurvePointsSize") * 1.75 # changing this value will impact how large the eye is, relative to your on-curve pt size

def eyelinerSymbolFactory(
        radius,
        stretch=0.7,
        strokeColor=(0, 0, 0, 1),
        strokeWidth=1
        ):
    # calcute the width and height
    width = radius * 6 * stretch * 2 + strokeWidth * 2
    height = radius * 2 + strokeWidth * 2
    # create a image draw bot 
    bot = NSImageDrawingTools((width, height))
    # get a pen
    pen = bot.BezierPath()
    # draw the eye
    pen.moveTo((6 * radius * stretch, 0))
    pen.curveTo(
        (2 * radius * stretch, 0),
        (1.25 * radius * stretch, -radius),
        (0, -radius))
    pen.curveTo(
        (-1.25 * radius * stretch, -radius),
        (-2 * radius * stretch, 0),
        (-6 * radius * stretch, 0))
    pen.curveTo(
        (-2 * radius * stretch, 0),
        (-1.25 * radius * stretch, radius),
        (0, radius))
    pen.curveTo(
        (1.25 * radius * stretch, radius),
        (2 * radius * stretch, 0),
        (6 * radius * stretch, 0))
    pen.closePath()

    bot.fill(None)
    bot.stroke(*strokeColor)
    bot.strokeWidth(strokeWidth)
    bot.translate(width / 2, height / 2)
    bot.drawPath(pen)
    # return the image
    return bot.getImage()
    
merz.SymbolImageVendor.registerImageFactory("eyeliner.eye", eyelinerSymbolFactory)



class Eyeliner(Subscriber):

    def started(self):
        try:
            self.g = CurrentGlyph()
        except:
            self.g = None
            
        self.col_font_dim = self.getFlattenedAlpha(
            NSColorToRgba(getDefaultColor("glyphViewFontMetricsStrokeColor")))
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
        
    def glyphEditorDidOpen(self, info):
        self.bgContainer = info['glyphEditor'].extensionContainer(
            identifier="eyeliner.background", 
            location="background", 
            clear=True
            )
        
    def beginDrawing(self):
        if self.g == None:
            return
        self.f = self.g.font
            
        self.bgContainer.clearSublayers()

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
            
        eye = self.bgContainer.appendSymbolSublayer(
                position        = (x, y),
                rotation        = angle,
                imageSettings   = dict(
                                    name        = "eyeliner.eye",
                                    radius      = rad_base, 
                                    strokeColor = color       
                                    )
                )
        
        
registerGlyphEditorSubscriber(Eyeliner)