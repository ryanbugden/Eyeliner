import math
from colorsys import rgb_to_hsv, hsv_to_rgb
from lib.tools.defaults import getDefault
from fontTools.misc.fixedTools import otRound

from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber
from  mojo.tools import IntersectGlyphWithLine
from mojo.UI import CurrentGlyphWindow, getGlyphViewDisplaySettings
from mojo.pens import DecomposePointPen

import merz
from merz.tools.drawingTools import NSImageDrawingTools


POINT_RADIUS = getDefault("glyphViewOnCurvePointsSize")
RAD_BASE = POINT_RADIUS * 1.75  # Changing this value will impact how large the eye is, relative to your on-curve pt size

def eyelinerSymbolFactory(
        radius      = RAD_BASE,
        stretch     = 0.7,
        strokeColor = (0, 0, 0, 1),
        strokeWidth = 1,
        fillColor   = (1, 1, 1, 0)
        ):
    # Calcute the width and height
    width  = radius * 6 * stretch * 2 + strokeWidth * 2
    height = radius * 2 + strokeWidth * 2
    # Create a image draw bot 
    bot = NSImageDrawingTools((width, height))
    # Get a pen
    pen = bot.BezierPath()
    # Draw the eye
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

    bot.fill(*fillColor)
    bot.stroke(*strokeColor)
    bot.strokeWidth(strokeWidth)
    bot.translate(width / 2 + 0.25, height / 2 + 0.25)
    bot.drawPath(pen)
    
    return bot.getImage()  # Return the image
    
merz.SymbolImageVendor.registerImageFactory("eyeliner.eye", eyelinerSymbolFactory)


def is_on_diagonal(pta, angle, ptb, tol=0.11):
    if pta == ptb: 
        return True
    ar = math.radians(angle)%math.pi
    ca = math.cos(ar)
    sa = math.sin(ar)
    if not math.isclose(ca,0,abs_tol=tol) and not math.isclose(sa,0,abs_tol=tol):
        # diagonal, distances for x and y should match
        tdx = (pta[0]-ptb[0])/ca
        tdy = (pta[1]-ptb[1])/sa
        return math.isclose(tdx, tdy, abs_tol=2)
    elif math.isclose(ca,1,abs_tol=tol) and math.isclose(sa,0,abs_tol=tol):
        # horizontal, so y should match
        return math.isclose(pta[1], ptb[1], abs_tol=tol)
    elif math.isclose(ca,0,abs_tol=tol) and math.isclose(sa,1,abs_tol=tol):
        # vertical, so x should match
        return math.isclose(pta[0], ptb[0], abs_tol=tol)
    return False


# # Draw the eye perfectly on the diagonal. Keeps input pt x
# def get_diagonal_xy(pta, angle, ptb):
#     if pta == ptb: 
#         return ptb[1]

#     y_off = math.tan(math.radians(angle)) * (ptb[0]- pta[0])
#     y_from_x = pta[1] + y_off

#     x_off =  (ptb[1]- pta[1])/ math.tan(math.radians(angle)) 
#     x_from_y = pta[0] + x_off

#     if abs(x_from_y - ptb[0]) > abs(y_from_x - ptb[1]):
#         diag_x, diag_y = x_from_y, ptb[1]
#     else:
#         diag_x, diag_y = ptb[0], y_from_x

#     return diag_x, diag_y


class Eyeliner(Subscriber):

    def build(self):
        self.slice_tool_active = False
        self.slice_coords = []


    def started(self):
        try:
            self.g = CurrentGlyph()
        except:
            self.g = None
        self.update_color_prefs()

        self.container = self.getGlyphEditor().extensionContainer(
            identifier="eyeliner.foreground", 
            location="foreground", 
            clear=True
            )

        self.begin_drawing()
        
        
    def destroy(self):
        self.container.clearSublayers()
        
        
    def roboFontDidChangePreferences(self, info):
        self.update_color_prefs()


    def update_color_prefs(self):
        self.gvbc = getDefault("glyphViewBackgroundColor")
        self.gvmc = getDefault("glyphViewMarginColor")
            
        self.col_font_dim = self.get_flattened_alpha(getDefault("glyphViewFontMetricsStrokeColor"))
        self.col_glob_guides = self.get_flattened_alpha(getDefault("glyphViewGlobalGuidesColor"))
        self.col_loc_guides = self.get_flattened_alpha(getDefault("glyphViewLocalGuidesColor"))

        self.col_blues = self.get_darkened_blue(self.get_flattened_alpha(getDefault("glyphViewBluesColor")))
        self.col_fblues = self.get_darkened_blue(self.get_flattened_alpha(getDefault("glyphViewFamilyBluesColor")))
        
        self.component_color = self.get_flattened_alpha(getDefault("glyphViewComponentStrokeColor"))


    def get_flattened_alpha(self, color):
        # Flatten transparency of eye, using background color preference
        r, g, b, a = color
        r2, g2, b2, a2 = self.gvbc
        r3 = r2 + (r - r2) * a
        g3 = g2 + (g - g2) * a
        b3 = b2 + (b - b2) * a
        
        return (r3, g3, b3, 1)
        

    def get_darkened_blue(self, color):
        # Darkened version of non-transparent blue zone color preference
        r, g, b, a = color
        h, s, v    = rgb_to_hsv(r*255, g*255, b*255)
        r, g, b    = hsv_to_rgb(h, s + (1 - s)/2, v*0.6)
        
        return (r/255, g/255, b/255, 1)

    
    def glyphEditorGlyphDidChange(self, info):
        self.g = info["glyph"]
        self.begin_drawing()
        
        
    def glyphEditorDidSetGlyph(self, info):
        self.g = info["glyph"]
        self.begin_drawing() 
        
        
    def glyphEditorDidMouseDown(self, info):
        '''Support for slice tool eyes'''
        lle = info['lowLevelEvents'][0]
        tool = lle ['tool']
        self.down_point = lle['point']
        if tool.__module__ == "lib.eventTools.sliceTool":
            self.slice_tool_active = True
        else:
            self.slice_tool_active = False
        
        
    def glyphEditorDidMouseDrag(self, info):
        self.g = info["glyph"]
        
        self.slice_coords = []
        if self.slice_tool_active:
            slice_line = (self.down_point, info['lowLevelEvents'][0]['point'])
            intersects = IntersectGlyphWithLine(self.g, slice_line, canHaveComponent=False, addSideBearings=False)
            for inter in intersects:
                x, y = otRound(inter[0]), otRound(inter[1])
                self.slice_coords.append((x,y))
        else:
            self.slice_coords = []
        
        self.begin_drawing()
        

    def begin_drawing(self):
        if self.g == None:
            return
        self.f = self.g.font
        
        # Use a decomposed version of the current glyph in order to analyze.
        decomp_glyph = RGlyph()
        decomp_glyph.width = self.g.width
        decomp_pen = DecomposePointPen(self.f, decomp_glyph.getPointPen())
        self.g.drawPoints(decomp_pen)
            
        self.container.clearSublayers()

        oncurves_on = getGlyphViewDisplaySettings().get('OnCurvePoints')
        anchors_on  = getGlyphViewDisplaySettings().get('Anchors')
        
        # On-curve points
        real_points = []
        if oncurves_on is True:
            for c in self.g.contours:
                for pt in c.points:
                    if pt.type != 'offcurve':
                        self.check_metrics(pt.x, pt.y)
                        real_points.append((pt.x, pt.y))
                        
        # Anchors (Use un-decomposed glyph)
        if anchors_on is True:
            for a in self.g.anchors:
                self.check_metrics(a.x, a.y)
                
        # Slice tool intersections
        if self.slice_tool_active:
            for (x,y) in self.slice_coords:
                self.check_metrics(x, y)
                
        # Component points
        for c in decomp_glyph.contours:
            for pt in c.points:
                if pt.type != 'offcurve':
                    if (pt.x, pt.y) not in real_points:
                        if self.check_metrics(pt.x, pt.y) == True:
                            self.draw_component_point(pt.x, pt.y)
                
                
    def check_metrics(self, x, y):
        metrics_match = False
        
        # Get font dimensions y's
        font_dim = [
            self.f.info.descender, 0, self.f.info.xHeight,
            self.f.info.ascender, self.f.info.capHeight
            ]
        
        # Get guide x's and y's
        f_guide_xs    = {}
        f_guide_ys    = {}
        f_guide_diags = []
        for guideline in self.f.guidelines:
            if guideline.angle in [0, 180]:
                f_guide_ys[otRound(guideline.y)] = guideline.color
            elif guideline.angle in [90, 270]:
                f_guide_xs[otRound(guideline.x)] = guideline.color
            else:
                f_guide_diags.append(guideline)
        
        # Get blue y's and whether they're set to be displayed
        blue_vals = self.f.info.postscriptBlueValues + self.f.info.postscriptOtherBlues
        fblue_vals = self.f.info.postscriptFamilyBlues + self.f.info.postscriptFamilyOtherBlues
        
        blues_on = getGlyphViewDisplaySettings()['Blues']
        fblues_on = getGlyphViewDisplaySettings()['FamilyBlues']

        if self.g is not None:

            g_guide_xs    = {}
            g_guide_ys    = {}
            g_guide_diags = []
            for guideline in self.g.guidelines:
                if guideline.angle in [0, 180]:
                    g_guide_ys[otRound(guideline.y)] = guideline.color
                elif guideline.angle in [90, 270]:
                    g_guide_xs[otRound(guideline.x)] = guideline.color
                else:
                    g_guide_diags.append(guideline)

            angle = 0
            color = None

            # ==== HORIZONTAL STUFF ==== #
            # Global horizontal guides
            if otRound(y) in f_guide_ys.keys():
                color = f_guide_ys[otRound(y)]
                if color is None:
                    color = self.col_glob_guides
                self.draw_eye(x, y, color, angle)
                metrics_match = True

            # Local horizontal guides
            elif otRound(y) in g_guide_ys.keys():
                color = g_guide_ys[otRound(y)]
                if color is None:
                    color = self.col_loc_guides
                self.draw_eye(x, y, color, angle)
                metrics_match = True

            # Font dimensions
            elif otRound(y) in font_dim:
                color = self.col_font_dim
                self.draw_eye(x, y, color, angle)
                metrics_match = True

            # Blues
            elif otRound(y) in blue_vals:
                if blues_on is True:
                    color = self.col_blues
                    self.draw_eye(x, y, color, angle)

            # Family blues
            elif otRound(y) in fblue_vals:
                if fblues_on is True:
                    color = self.col_fblues
                    self.draw_eye(x, y, color, angle)
                    metrics_match = True

            # ==== VERTICAL STUFF ==== #
            angle = 90
            # Global vertical guides
            if otRound(x) in f_guide_xs.keys():
                color = f_guide_xs[otRound(x)]
                if color is None:
                    color = self.col_glob_guides
                self.draw_eye(x, y, color, angle)
                metrics_match = True

            # Local vertical guides
            elif otRound(x) in g_guide_xs.keys():
                color = g_guide_xs[otRound(x)]
                if color is None:
                    color = self.col_loc_guides
                self.draw_eye(x, y, color, angle)
                metrics_match = True

            # ==== DIAGONAL STUFF ==== #
            for gd in g_guide_diags + f_guide_diags:
                color = gd.color
                if color is None:
                    if gd in g_guide_diags:
                        color = self.col_loc_guides 
                    else:
                        color = self.col_glob_guides 
                angle = gd.angle
                result = is_on_diagonal((gd.x, gd.y), angle, (x, y))
                if result:
                    ## Tested code to clean up the diagonal eye presentation
                    # diag_x, diag_y = get_diagonal_xy((gd.x, gd.y), angle, (x, y))  # Try to avoid the eye looking disjointed from the guide.
                    self.draw_eye(x, y, color, angle)
                    metrics_match = True
                    
        return metrics_match
                
                
    def draw_eye(self, x, y, color, angle):

        # # Stored attempt at creating an illusion of line diverging and converging, using fill color. Would only work on unsupported z-index.
        # self.fill_color = self.gvbc
        # if x < 0 or x > self.g.width:
        #     self.fill_color = self.gvmc
            
        eye = self.container.appendSymbolSublayer(
                position        = (x, y),
                rotation        = angle,
                imageSettings   = dict(
                                    name        = "eyeliner.eye",
                                    radius      = RAD_BASE, 
                                    strokeColor = color,
                                    fillColor   = (1,1,1,0)  # self.fill_color
                                    )
                )
                
                
    def draw_component_point(self, x, y):
        component_point = self.container.appendSymbolSublayer(
                position=(x, y)
                )

        component_point.setImageSettings(
                dict(
                    name="oval",
                    size=(otRound(POINT_RADIUS*2), otRound(POINT_RADIUS*2)),
                    fillColor=tuple(self.component_color)
                )
            )
        
        
registerGlyphEditorSubscriber(Eyeliner)
