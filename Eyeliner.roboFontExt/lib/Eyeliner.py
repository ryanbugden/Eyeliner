from mojo.events import addObserver
from mojo.drawingTools import *
from lib.tools.defaults import getDefaultColor, getDefault
from mojo.UI import getGlyphViewDisplaySettings
from lib.tools.misc import NSColorToRgba
from fontTools.misc.fixedTools import otRound

rad_base = getDefault("glyphViewOncurvePointsSize") * 1.7

class Eyeliner():
    
    '''
    Adds a little eye around points that are on the font’s vertical dimensions or guidelines.
    
    Ryan Bugden
    v1.2.1 : 2020.04.03
    v1.2.0 : 2020.03.26
    v1.1.1 : 2020.01.27
    v1.0.0 : 2020.01.24
    v0.9.0 : 2019.06.04
    '''
    
    def __init__(self):
        
        self.col_vert_metrics = NSColorToRgba(getDefaultColor("glyphViewMetricsColor"))
        self.col_glob_guides = NSColorToRgba(getDefaultColor("glyphViewGlobalGuidesColor"))
        self.col_loc_guides = NSColorToRgba(getDefaultColor("glyphViewLocalGuidesColor"))
        
        col_blues = getDefaultColor("glyphViewBluesColor")
        self.col_blues = (col_blues.redComponent(), col_blues.greenComponent(), col_blues.blueComponent(), 1)
        
        col_fBlues = getDefaultColor("glyphViewFamilyBluesColor")
        self.col_fBlues = (col_fBlues.redComponent(), col_fBlues.greenComponent(), col_fBlues.blueComponent(), 1)
                
        self.scale = 0
        self.radius = 0
        
        addObserver(self, "drawBackground", "drawBackground")
        addObserver(self, "drawBackground", "drawBackgroundInactive")
        
        
    def drawBackground(self, notification):
        
        g = notification["glyph"]
        f = g.font
        
        self.scale = notification['scale']
        self.radius = rad_base * self.scale
        
        # get vertical metrics y's
        vert_metrics = [f.info.descender, 0, f.info.xHeight, f.info.ascender, f.info.capHeight]
        # get guide x's and y's
        f_guide_xs   = {}
        f_guide_ys   = {}
        for guideline in f.guidelines:
            if guideline.angle == 0:
                f_guide_ys[otRound(guideline.y)] = guideline.color
            elif guideline.angle == 90:
                f_guide_xs[otRound(guideline.x)] = guideline.color
        # get blue y's
        blue_vals = f.info.postscriptBlueValues + f.info.postscriptOtherBlues
        fBlue_vals = f.info.postscriptFamilyBlues + f.info.postscriptFamilyOtherBlues
        blues_on  = getGlyphViewDisplaySettings()['Blues']
        fBlues_on = getGlyphViewDisplaySettings()['Family Blues']
        
        if g != None:
            
            g_guide_xs   = {}
            g_guide_ys   = {}
            for guideline in g.guidelines:
                if guideline.angle == 0:
                    g_guide_ys[otRound(guideline.y)] = guideline.color
                elif guideline.angle == 90:
                    g_guide_xs[otRound(guideline.x)] = guideline.color
                    
            for c in g:
                for pt in c.points:
                    if pt.type != 'offcurve':
                        angle = 0
                        color = None
                        
                        # vertical metrics
                        if otRound(pt.y) in vert_metrics:
                            color = self.col_vert_metrics
                            self.drawEye(pt.x, pt.y, color, angle)  
                            
                        # global horizontal guides
                        elif otRound(pt.y) in f_guide_ys.keys():
                            color = f_guide_ys[otRound(pt.y)]
                            if color == None:
                                color = self.col_glob_guides
                            self.drawEye(pt.x, pt.y, color, angle)  
                            
                        # local horizontal guides
                        elif otRound(pt.y) in g_guide_ys.keys():
                            color = g_guide_ys[otRound(pt.y)]
                            if color == None:
                                color = self.col_loc_guides
                            self.drawEye(pt.x, pt.y, color, angle)
                            
                        # blues
                        elif otRound(pt.y) in blue_vals:
                            if blues_on == True:
                                color = self.col_blues
                                self.drawEye(pt.x, pt.y, color, angle) 
                            
                        # family blues
                        elif otRound(pt.y) in fBlue_vals:
                            if fBlues_on == True:
                                color = self.col_fBlues
                                self.drawEye(pt.x, pt.y, color, angle) 
                        
                        # global vertical guides        
                        if otRound(pt.x) in f_guide_xs.keys():
                            angle = 90
                            color = f_guide_xs[otRound(pt.x)]
                            if color == None:
                                color = self.col_glob_guides
                            self.drawEye(pt.x, pt.y, color, angle)
                            
                        # local vertical guides        
                        elif otRound(pt.x) in g_guide_xs.keys():
                            angle = 90
                            color = g_guide_xs[otRound(pt.x)]
                            if color == None:
                                color = self.col_loc_guides
                            self.drawEye(pt.x, pt.y, color, angle)
                            
                        
                                                               
                                    
                        
    def drawEye(self, x, y, color, angle):
        
        stretch = 0.7
        save()
        # rounding the eye to nearest unit even though point might not be:
        translate(otRound(x), otRound(y))
        rotate(angle)
        
        fill(None)
        strokeWidth(self.scale/2)
        stroke(*color)
        
        newPath()
        moveTo((6*self.radius*stretch, 0))
        curveTo((2*self.radius*stretch, 0), (1.25*self.radius*stretch, -self.radius), (0, -self.radius))
        curveTo((-1.25*self.radius*stretch, -self.radius), (-2*self.radius, 0), (-6*self.radius*stretch, 0))
        curveTo((-2*self.radius*stretch, 0), (-1.25*self.radius*stretch, self.radius), (0, self.radius))
        curveTo((1.25*self.radius*stretch, self.radius), (2*self.radius*stretch, 0), (6*self.radius*stretch, 0))
        drawPath()
        closePath()
        restore()

            
Eyeliner()