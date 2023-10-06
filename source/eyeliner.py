import math
from colorsys import rgb_to_hsv, hsv_to_rgb
from fontTools.misc.fixedTools import otRound
from fontParts.world import RGlyph

from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber
from mojo.tools import IntersectGlyphWithLine
from mojo.UI import CurrentGlyphWindow, getGlyphViewDisplaySettings, getDefault, appearanceColorKey
from mojo.pens import DecomposePointPen
from fontPens.digestPointPen import DigestPointPen

import merz
from merz.tools.drawingTools import NSImageDrawingTools


def eyeliner_symbol(
        radius      = 5,
        stretch     = 0.7,
        strokeColor = (0, 0, 0, 1),
        strokeWidth = 1,
        fillColor   = (1, 1, 1, 0)
        ):
    # Calculate the width and height
    width  = radius * 6 * stretch * 2 + strokeWidth * 2
    height = radius * 2 + strokeWidth * 2
    # Create a NSImage drawing bot 
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
    return bot.getImage()
    
merz.SymbolImageVendor.registerImageFactory("eyeliner.eye", eyeliner_symbol)


def is_on_diagonal(pta, angle, ptb, tol=0.08):
    if pta == ptb: 
        return True
        
    ar = math.radians(angle)%math.pi
    ca = math.cos(ar)
    sa = math.sin(ar)
    x_diff = ptb[0] - pta[0]
    y_diff = ptb[1] - pta[1]

    if not math.isclose(ca, 0, abs_tol=tol) and not math.isclose(sa, 0, abs_tol=tol):
        # Diagonal, distances for x and y should match
        tdx = x_diff / ca
        tdy = y_diff / sa
        return math.isclose(tdx, tdy, abs_tol=5)
        
    elif math.isclose(ca, 1, abs_tol=tol) and math.isclose(sa, 0, abs_tol=tol):
        # Horizontal, so y should match
        return math.isclose(pta[1], ptb[1], abs_tol=tol)
        
    elif math.isclose(ca, 0, abs_tol=tol) and math.isclose(sa, 1, abs_tol=tol):
        # Vertical, so x should match
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
        self.font_dim = []
        self.tool_coords = []
        self.oncurve_coords = []
        self.comp_oncurve_coords = []
        self.transm_oncurve_coords = []

        self.anc_coords = []

        self.slice_tool = None
        self.shape_tool = None
        self.transmutor_tool = None
        self.slice_tool_active = False
        self.shape_tool_active = False
        self.transmutor_active = False

        self.down_point, self.drag_point = (0,0), (0,0)
        self.blue_vals, self.fblue_vals = [], []

        self.update_base_sizes()
        self.update_blues_display_settings()
        self.oncurves_on = getGlyphViewDisplaySettings().get('OnCurvePoints')
        self.anchors_on = getGlyphViewDisplaySettings().get('Anchors')

        self.glyph_editor = self.getGlyphEditor()
        
        self.oncurve_container = self.glyph_editor.extensionContainer(
                    identifier="eyeliner.oncurves", 
                    location="foreground", 
                    clear=True
                )
        self.comp_container = self.glyph_editor.extensionContainer(
                    identifier="eyeliner.components", 
                    location="foreground", 
                    clear=True
                )
        self.anchor_container = self.glyph_editor.extensionContainer(
                    identifier="eyeliner.anchors", 
                    location="foreground", 
                    clear=True
                )
        self.tool_container = self.glyph_editor.extensionContainer(
                    identifier="eyeliner.slice", 
                    location="foreground", 
                    clear=True
                )
        

    def started(self):
        try:
            self.g = self.glyph_editor.getGlyph()
            self.update_font_info()
        except:
            self.g = None
        self.update_color_prefs()
        
        self.check_oncurves()
        self.check_anchors()
        self.check_comp()
        
        
    def destroy(self):
        self.oncurve_container.clearSublayers()
        self.comp_container.clearSublayers()
        self.anchor_container.clearSublayers()
        self.tool_container.clearSublayers()
        

    def update_base_sizes(self):
        self.point_radius = getDefault("glyphViewOnCurvePointsSize")
        self.rad_base = self.point_radius * 1.75  # Changing this value will impact how large the eye is, relative to your on-curve pt size


    def update_color_prefs(self):
        self.gvbc = getDefault("glyphViewBackgroundColor")
        self.gvmc = getDefault("glyphViewMarginColor")
            
        self.col_font_dim = self.get_flattened_alpha(getDefault(appearanceColorKey("glyphViewFontMetricsStrokeColor")))
        self.col_glob_guides = self.get_flattened_alpha(getDefault(appearanceColorKey("glyphViewGlobalGuidesColor")))
        self.col_loc_guides = self.get_flattened_alpha(getDefault(appearanceColorKey("glyphViewLocalGuidesColor")))

        self.col_blues = self.get_darkened_blue(self.get_flattened_alpha(getDefault(appearanceColorKey("glyphViewBluesColor"))))
        self.col_fblues = self.get_darkened_blue(self.get_flattened_alpha(getDefault(appearanceColorKey("glyphViewFamilyBluesColor"))))
        
        self.col_component = self.get_flattened_alpha(getDefault(appearanceColorKey("glyphViewComponentStrokeColor")))

        self.col_corner_pt = self.get_flattened_alpha(getDefault(appearanceColorKey("glyphViewCornerPointsFill")))
        self.col_curve_pt = self.get_flattened_alpha(getDefault(appearanceColorKey("glyphViewCurvePointsFill")))


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

        
    def roboFontDidChangePreferences(self, info):
        self.update_color_prefs()
        self.update_base_sizes()


    def roboFontAppearanceChanged(self, info):
        self.update_color_prefs()
        # Update guidelines have color attribute, so update that info, and check things against it.
        self.update_guidelines_info()
        self.check_oncurves()
        self.check_anchors()
        self.check_comp()


    glyphEditorGlyphDidChangeOutlineDelay = 0
    def glyphEditorGlyphDidChangeOutline(self, info):
        self.g = info["glyph"]
        self.update_oncurve_info()
        self.check_oncurves()


    glyphEditorGlyphDidChangeContoursDelay = 0    
    def glyphEditorGlyphDidChangeContours(self, info):
        self.g = info["glyph"]
        self.update_oncurve_info()
        self.check_oncurves()


    glyphEditorGlyphDidChangeComponentsDelay = 0
    def glyphEditorGlyphDidChangeComponents(self, info):
        self.g = info["glyph"]
        self.update_component_info()
        self.check_comp()


    glyphEditorGlyphDidChangeAnchorsDelay = 0
    def glyphEditorGlyphDidChangeAnchors(self, info):
        self.g = info["glyph"]
        self.update_anchor_info()
        self.check_anchors()


    glyphEditorGlyphDidChangeGuidelinesDelay = 0
    def glyphEditorGlyphDidChangeGuidelines(self, info):
        self.g = info["glyph"]
        self.update_guidelines_info()
        self.check_oncurves()
        self.check_anchors()
        self.check_comp()


    glyphEditorFontDidChangeGuidelinesDelay = 0
    def glyphEditorFontDidChangeGuidelines(self, info):
        self.f = info["font"]
        self.update_guidelines_info()
        self.check_oncurves()
        self.check_anchors()
        self.check_comp()


    glyphEditorDidSetGlyphDelay = 0.0001
    def glyphEditorDidSetGlyph(self, info):
        self.g = info["glyph"]
        # Update on-curves before component info.
        self.update_oncurve_info()
        self.update_component_info()
        self.update_anchor_info()
        self.update_guidelines_info()
        self.check_oncurves()
        self.check_anchors()
        self.check_comp()
        
        
    def glyphEditorDidMouseDown(self, info):
        '''Support for slice/shape tool eyes'''
        tool = info['lowLevelEvents'][0]['tool']
        
        if tool.__class__.__name__ == "SliceTool":
            self.slice_tool_active = True
            self.shape_tool_active = False
            self.transmutor_active = False
            self.slice_tool = tool
            point = self.slice_tool.sliceDown
            self.down_point = (point.x, point.y)
        elif tool.__class__.__name__ == "DrawGeometricShapesTool":
            self.slice_tool_active = False
            self.shape_tool_active = True
            self.transmutor_active = False
            self.shape_tool = tool
        elif tool.__class__.__name__ == "TransmutorToolController":
            self.slice_tool_active = False
            self.shape_tool_active = False
            self.transmutor_active = True
            self.transmutor_tool = tool
        else:
            self.slice_tool_active = False
            self.shape_tool_active = False
            self.transmutor_active = False
            
        self.check_tool_points()
        
        
    def glyphEditorDidMouseDrag(self, info):
        '''Support for slice/shape tool eyes'''
        self.g = info["glyph"]
        
        self.tool_coords = []
        # Slice tool
        if self.slice_tool_active:
            point = self.slice_tool.sliceDrag
            if point:
                self.drag_point = (point.x, point.y)
                slice_line = (self.down_point, self.drag_point)
                intersects = IntersectGlyphWithLine(self.g, slice_line, canHaveComponent=False, addSideBearings=False)
                for inter in intersects:
                    x, y = otRound(inter[0]), otRound(inter[1])
                    self.tool_coords.append((x,y)) 
            else:
                self.tool_coords = []
        # Shape tool
        elif self.shape_tool_active:
            if not self.shape_tool.getRect():
                self.tool_coords = []
                self.check_tool_points()
                return
            tx, ty, tw, th = self.shape_tool.getRect()
            if self.shape_tool.shape == "rect":
                self.shape_pt_color = self.col_corner_pt
                self.shape_pt_shape = "rectangle"
                self.tool_coords = [
                        (tx, ty),
                        (tx + tw, ty),
                        (tx, ty + th),
                        (tx + tw, ty + th),
                    ]    
            elif self.shape_tool.shape == "oval":
                self.shape_pt_color = self.col_curve_pt
                self.shape_pt_shape = "oval"
                self.tool_coords = [
                        ((tx*2 + tw)/2, ty),
                        (tx + tw, (ty*2 + th)/2),
                        ((tx*2 + tw)/2, ty + th),
                        (tx, (ty*2 + th)/2),
                    ] 
            # Round the points
            for i, (coord_x, coord_y) in enumerate(self.tool_coords):
                self.tool_coords[i] = (otRound(coord_x), otRound(coord_y))
        # Transmutor
        elif self.transmutor_active:
            model = self.transmutor_tool.model
            if model:
                self.transmutor_color = model.scaledGlyphColor
                scaled_glyph = model.getScaledGlyph()
                if scaled_glyph:
                    scaled_glyph.moveBy((model.offsetX, model.offsetY))
                    digest_pen = DigestPointPen()
                    scaled_glyph.drawPoints(digest_pen)
                    self.tool_coords = [entry[0] for entry in digest_pen.getDigest() if entry[1] != None and type(entry[0]) == tuple and entry[0] not in self.tool_coords] 
                    self.tool_coords = [(otRound(x), otRound(y)) for (x, y) in self.tool_coords]
            else:
                self.tool_coords = []
        else:
            self.tool_coords = []
        
        self.check_tool_points()
        
        
    def glyphEditorDidMouseUp(self, info):
        '''Support for slice/shape tool eyes'''
        # Remove eyes on undo
        self.slice_tool_active = False
        self.shape_tool_active = False
        # We want the points to remain on mouse-up with Transmutor
        if not self.transmutor_active:
            self.tool_coords = []
        self.check_tool_points()


    glyphEditorFontInfoDidChangeDelay = 0.1
    def glyphEditorFontInfoDidChange(self, info):
        self.update_font_info()


    def update_component_info(self):
        self.f = self.g.font

        # Set up a decomposed glyph object
        self.decomp_glyph = RGlyph()
        self.decomp_glyph.width = self.g.width
        decomp_pen = DecomposePointPen(self.f, self.decomp_glyph.getPointPen())
        self.g.drawPoints(decomp_pen)
        # Get all on-curve points for the component, and nothing else
        digest_pen = DigestPointPen()
        self.decomp_glyph.drawPoints(digest_pen)
        self.comp_oncurve_coords = [entry[0] for entry in digest_pen.getDigest() if entry[1] != None and type(entry[0]) == tuple and entry[0] not in self.oncurve_coords] 


    def update_oncurve_info(self):
        self.oncurves_on = getGlyphViewDisplaySettings().get('OnCurvePoints')
        # Use a digest point pen to get only on-curves
        digest_pen = DigestPointPen()
        self.g.drawPoints(digest_pen)
        # Get all on-curve points
        self.oncurve_coords = [entry[0] for entry in digest_pen.getDigest() if entry[1] != None and type(entry[0]) == tuple] 


    def update_anchor_info(self):
        '''Store updated anchor coordinates'''
        self.anchors_on = getGlyphViewDisplaySettings().get('Anchors')
        self.anc_coords = [(a.x, a.y) for a in self.g.anchors]


    def update_guidelines_info(self):
        '''Store updated guideline coordinates'''
        # Font guidelines
        self.f_guide_xs    = {}
        self.f_guide_ys    = {}
        self.f_guide_diags = []
        for guideline in self.f.guidelines:
            if guideline.color:
                guide_color = guideline.color
            else:
                guide_color = self.col_glob_guides
            if guideline.angle in [0, 180]:
                self.f_guide_ys[otRound(guideline.y)] = guide_color
            elif guideline.angle in [90, 270]:
                self.f_guide_xs[otRound(guideline.x)] = guide_color
            else:
                self.f_guide_diags.append(((guideline.x, guideline.y), guideline.angle, guide_color))

        # Glyph guidelines
        if self.g is not None:
            self.g_guide_xs    = {}
            self.g_guide_ys    = {}
            self.g_guide_diags = []
            for guideline in self.g.guidelines:
                if guideline.color:
                    guide_color = guideline.color
                else:
                    guide_color = self.col_loc_guides
                if guideline.angle in [0, 180]:
                    self.g_guide_ys[otRound(guideline.y)] = guide_color
                elif guideline.angle in [90, 270]:
                    self.g_guide_xs[otRound(guideline.x)] = guide_color
                else:
                    self.g_guide_diags.append(((guideline.x, guideline.y), guideline.angle, guide_color))
        
        
    def update_font_info(self):
        self.f = self.g.font
        # Get font dimensions y's
        self.font_dim = [
            self.f.info.descender, 0, self.f.info.xHeight,
            self.f.info.ascender, self.f.info.capHeight
            ]
        
        # Get blue y's and whether they're set to be displayed
        self.blue_vals  = self.f.info.postscriptBlueValues + self.f.info.postscriptOtherBlues
        self.fblue_vals = self.f.info.postscriptFamilyBlues + self.f.info.postscriptFamilyOtherBlues
        self.update_blues_display_settings()


    def update_blues_display_settings(self):
        self.blues_on  = getGlyphViewDisplaySettings()['Blues']
        self.fblues_on = getGlyphViewDisplaySettings()['FamilyBlues']


    def check_oncurves(self):
        if self.g == None:
            return
        self.oncurve_container.clearSublayers()
        # On-curve points
        if self.oncurves_on is True:
            for coord in self.oncurve_coords:
                self.check_alignment(self.oncurve_container, coord)

                     
    def check_anchors(self):   
        if self.g == None:
            return
        self.anchor_container.clearSublayers()
        # Anchors
        if self.anchors_on is True:
            for coord in self.anc_coords:
                self.check_alignment(self.anchor_container, coord)

                
    def check_tool_points(self):
        if self.g == None:
            return
        self.tool_container.clearSublayers()
        # Slice tool intersections
        if self.slice_tool_active:
            for coord in self.tool_coords:
                self.check_alignment(self.tool_container, coord)
        # Shape tool future points
        elif self.shape_tool_active:
            for coord in self.tool_coords:
                if self.check_alignment(self.tool_container, coord) == True:
                    self.draw_oncurve_pt(self.tool_container, coord, self.shape_pt_color, self.shape_pt_shape)
        # Transmutor future points
        elif self.transmutor_active:
            for coord in self.tool_coords:
                if self.check_alignment(self.tool_container, coord) == True:
                    self.draw_oncurve_pt(self.tool_container, coord, self.transmutor_color, "oval")
                

    def check_comp(self):
        if self.g == None:
            return
        self.comp_container.clearSublayers()
        # Component points
        for coord in self.comp_oncurve_coords:
            if self.check_alignment(self.comp_container, coord) == True:
                self.draw_oncurve_pt(self.comp_container, coord, self.col_component, "oval")
                
                
    def check_alignment(self, container, coord):
        alignment_match = False
        x, y = coord[0], coord[1]

        if self.g is not None:

            angle = 0
            color = None

            # ==== HORIZONTAL STUFF ==== #
            # Global horizontal guides
            if otRound(y) in self.f_guide_ys.keys():
                color = self.f_guide_ys[otRound(y)]
                self.draw_eye(container, coord, color, angle)
                alignment_match = True

            # Local horizontal guides
            elif otRound(y) in self.g_guide_ys.keys():
                color = self.g_guide_ys[otRound(y)]
                self.draw_eye(container, coord, color, angle)
                alignment_match = True

            # Font dimensions
            elif otRound(y) in self.font_dim:
                color = self.col_font_dim
                self.draw_eye(container, coord, color, angle)
                alignment_match = True

            # Blues
            elif otRound(y) in self.blue_vals:
                if self.blues_on is True:
                    color = self.col_blues
                    self.draw_eye(container, coord, color, angle)
                    alignment_match = True

            # Family blues
            elif otRound(y) in self.fblue_vals:
                if self.fblues_on is True:
                    color = self.col_fblues
                    self.draw_eye(container, coord, color, angle)
                    alignment_match = True

            # ==== VERTICAL STUFF ==== #
            angle = 90
            # Global vertical guides
            if otRound(x) in self.f_guide_xs.keys():
                color = self.f_guide_xs[otRound(x)]
                self.draw_eye(container, coord, color, angle)
                alignment_match = True

            # Local vertical guides
            elif otRound(x) in self.g_guide_xs.keys():
                color = self.g_guide_xs[otRound(x)]
                self.draw_eye(container, coord, color, angle)
                alignment_match = True

            # ==== DIAGONAL STUFF ==== #
            for gd_info in self.g_guide_diags + self.f_guide_diags:
                angle, color = gd_info[1], gd_info[2]
                result = is_on_diagonal(gd_info[0], angle, (x, y))
                if result:
                    ## Tested code to clean up the diagonal eye presentation
                    # diag_x, diag_y = get_diagonal_xy((gd.x, gd.y), angle, (x, y))  # Try to avoid the eye looking disjointed from the guide.
                    self.draw_eye(container, coord, color, angle)
                    alignment_match = True
                    
        return alignment_match
                
                
    def draw_eye(self, container, coord, color, angle):
        eye = container.appendSymbolSublayer(
                position      = (coord[0], coord[1]),
                rotation      = angle,
                imageSettings = dict(
                                    name        = "eyeliner.eye",
                                    radius      = self.rad_base, 
                                    strokeColor = color,
                                    fillColor   = (1,1,1,0)  # self.fill_color
                                    )
                )
                
                
    def draw_oncurve_pt(self, container, coord, color, shape):
        component_point  = container.appendSymbolSublayer(
                position = (coord[0], coord[1])
                )
        component_point.setImageSettings(
                dict(
                    name      = shape,
                    size      = (otRound(self.point_radius*2), otRound(self.point_radius*2)),
                    fillColor = tuple(color)
                )
            )
        
        
registerGlyphEditorSubscriber(Eyeliner)
