import ezui
from colorsys import rgb_to_hsv, hsv_to_rgb
from mojo.extensions import getExtensionDefault, setExtensionDefault
from mojo.UI import getDefault



def get_flattened_alpha(color):
    # Flatten transparency of eye, using background color preference
    gvbc = getDefault("glyphViewBackgroundColor")
    r, g, b, a = color
    r2, g2, b2, a2 = gvbc
    r3 = r2 + (r - r2) * a
    g3 = g2 + (g - g2) * a
    b3 = b2 + (b - b2) * a
    return (r3, g3, b3, 1)

def get_darkened_blue(color):
    # Darkened version of non-transparent blue zone color preference
    r, g, b, a = color
    h, s, v    = rgb_to_hsv(r*255, g*255, b*255)
    r, g, b    = hsv_to_rgb(h, s + (1 - s)/2, v*0.6)
    
    return (r/255, g/255, b/255, 1)


EXTENSION_KEY = 'com.ryanbugden.eyeliner.settings'
EXTENSION_DEFAULTS = {
    "showFontDimensionsCheckbox": True,
    "fontDimensionsLightColorWell": get_flattened_alpha(getDefault("glyphViewFontMetricsStrokeColor")),
    "fontDimensionsDarkColorWell": get_flattened_alpha(getDefault("glyphViewFontMetricsStrokeColor.dark")),
    "showBluesCheckbox": True,
    "bluesLightColorWell": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewBluesColor"))),
    "bluesDarkColorWell": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewBluesColor.dark"))),
    "showFamilyBluesCheckbox": True,
    "familyBluesLightColorWell": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewFamilyBluesColor"))),
    "familyBluesDarkColorWell": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewFamilyBluesColor.dark"))),
    "showMarginsCheckbox": False,
    "marginsLightColorWell": (0,0,0,1),
    "marginsDarkColorWell": (1,1,1,1),
}


class EyelinerSettings(ezui.WindowController):

    def build(self):
        content = """

        * TwoColumnForm        @form1
        
        > : Show Eyes:
        > [X] Font Dimensions  @showFontDimensionsCheckbox
        > [X] Blue Zones       @showBluesCheckbox
        > [X] Family Blues     @showFamilyBluesCheckbox
        > [X] Margins          @showMarginsCheckbox
        
        ---
        
        * TwoColumnForm        @form2
        
        > : Font Dimensions:
        > * HorizontalStack    @fontDimensionsColorStack
        >> * ColorWell         @fontDimensionsLightColorWell
        >> * ColorWell         @fontDimensionsDarkColorWell

        > : Blue Zones:
        > * HorizontalStack    @bluesColorStack
        >> * ColorWell         @bluesLightColorWell
        >> * ColorWell         @bluesDarkColorWell

        > : Family Blues:
        > * HorizontalStack    @familyBluesColorStack
        >> * ColorWell         @familyBluesLightColorWell
        >> * ColorWell         @familyBluesDarkColorWell

        > : Margins:
        > * HorizontalStack    @marginsColorStack
        >> * ColorWell         @marginsLightColorWell
        >> * ColorWell         @marginsDarkColorWell
        
        > :
        > * HorizontalStack    @labelStack
        >> Light Mode          @lightModeLabel
        >> Dark Mode           @darkModeLabel
        
        > ---
        
        > (Reset Defaults)     @resetDefaultsButton
        """
        title_column_width = 120
        item_column_width = 160
        colorwell_width = item_column_width / 2 - 5
        colorwell_height = 20
        descriptionData = dict(
            form1=dict(
                titleColumnWidth=title_column_width,
                itemColumnWidth=item_column_width
            ),
            form2=dict(
                titleColumnWidth=title_column_width,
                itemColumnWidth=item_column_width
            ),
            form3=dict(
                titleColumnWidth=title_column_width,
                itemColumnWidth=item_column_width
            ),
            fontDimensionsLightColorWell=dict(
                width=colorwell_width,
                height=colorwell_height
            ),
            fontDimensionsDarkColorWell=dict(
                width=colorwell_width,
                height=colorwell_height
            ),
            bluesLightColorWell=dict(
                width=colorwell_width,
                height=colorwell_height
            ),
            bluesDarkColorWell=dict(
                width=colorwell_width,
                height=colorwell_height
            ),
            familyBluesLightColorWell=dict(
                width=colorwell_width,
                height=colorwell_height
            ),
            familyBluesDarkColorWell=dict(
                width=colorwell_width,
                height=colorwell_height
            ),
            marginsLightColorWell=dict(
                width=colorwell_width,
                height=colorwell_height
            ),
            marginsDarkColorWell=dict(
                width=colorwell_width,
                height=colorwell_height
            ),
            lightModeLabel=dict(
                width=colorwell_width,
                sizeStyle='mini',
            ),
            darkModeLabel=dict(
                width=colorwell_width,
                sizeStyle='mini',
            ),
            resetDefaultsButton=dict(
                width='fill'
            )

        )
        self.w = ezui.EZPanel(
            title="Eyeliner Settings",
            content=content,
            descriptionData=descriptionData,
            controller=self
        )
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        prefs = getExtensionDefault(EXTENSION_KEY, fallback=EXTENSION_DEFAULTS)
        try:
            self.w.setItemValues(prefs)
        except KeyError as e:
            print(f"Eyeliner Settings error: {e}")
        

    def started(self):
        self.w.open()
        
            
    def contentCallback(self, sender):
        setExtensionDefault(EXTENSION_KEY, self.w.getItemValues())
        
        
    def resetDefaultsButtonCallback(self, sender):
        print(self.w.getItemValues())
        self.w.setItemValues(EXTENSION_DEFAULTS)
        setExtensionDefault(EXTENSION_KEY, self.w.getItemValues())



EyelinerSettings()