import ezui
from colorsys import rgb_to_hsv, hsv_to_rgb
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

DEFAULT_COLORS = {
    "eyeliner_marginsLightColor": get_flattened_alpha(getDefault("glyphViewMarginColor")),
    "eyeliner_marginsDarkColor": get_flattened_alpha(getDefault("glyphViewMarginColor.dark")),
    "eyeliner_fontDimensionsLightColor": get_flattened_alpha(getDefault("glyphViewFontMetricsStrokeColor")),
    "eyeliner_fontDimensionsDarkColor": get_flattened_alpha(getDefault("glyphViewFontMetricsStrokeColor.dark")),
    "eyeliner_globalGuidesLightColor": get_flattened_alpha(getDefault("glyphViewGlobalGuidesColor")),
    "eyeliner_globalGuidesDarkColor": get_flattened_alpha(getDefault("glyphViewGlobalGuidesColor.dark")),
    "eyeliner_localGuidesLightColor": get_flattened_alpha(getDefault("glyphViewLocalGuidesColor")),
    "eyeliner_localGuidesDarkColor": get_flattened_alpha(getDefault("glyphViewLocalGuidesColor.dark")),
    "eyeliner_bluesLightColor": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewBluesColor"))),
    "eyeliner_bluesDarkColor": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewBluesColor.dark"))),
    "eyeliner_familyBluesLightColor": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewFamilyBluesColor"))),
    "eyeliner_familyBluesDarkColor": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewFamilyBluesColor.dark"))),
}

class DemoController(ezui.WindowController):

    def build(self):
        content = """
        * TwoColumnForm        @form1
        
        > : Eyes:
        > [X] Show             @showEyesCheckbox
        
        ---

        * TwoColumnForm        @form2
        
        > : Font Dimensions:
        > * VerticalStack
        >> [X] Show Eyes       @showFontDimensionsCheckbox
        >> [ ] Override Color  @fontDimensionsColorCheckbox
        >> * HorizontalStack   @fontDimensionsColorStack
        >>> * ColorWell        @fontDimensionsLightColorWell
        >>> * ColorWell        @fontDimensionsDarkColorWell
        
        > ---
        
        > : Local Guides:
        > * VerticalStack
        >> [X] Show Eyes       @showLocalGuidesCheckbox
        >> [ ] Override Color  @localGuidesColorCheckbox
        >> * HorizontalStack   @localGuidesColorStack
        >>> * ColorWell        @localGuidesLightColorWell
        >>> * ColorWell        @localGuidesDarkColorWell
        
        > ---
        
        > : Global Guides:
        > * VerticalStack
        >> [X] Show Eyes       @showGlobalGuidesCheckbox
        >> [ ] Override Color  @globalGuidesColorCheckbox
        >> * HorizontalStack   @globalGuidesColorStack
        >>> * ColorWell        @globalGuidesLightColorWell
        >>> * ColorWell        @globalGuidesDarkColorWell
        
        > ---
                
        > : Blue Zones:
        > * VerticalStack
        >> [X] Show Eyes       @showBluesCheckbox
        >> [ ] Override Color  @bluesColorCheckbox
        >> * HorizontalStack   @bluesColorStack
        >>> * ColorWell        @bluesLightColorWell
        >>> * ColorWell        @bluesDarkColorWell
        
        > ---

        > : Family Blue Zones:
        > * VerticalStack
        >> [X] Show Eyes       @showFamilyBluesCheckbox
        >> [ ] Override Color  @familyBluesColorCheckbox
        >> * HorizontalStack   @familyBluesColorStack
        >>> * ColorWell        @familyBluesLightColorWell
        >>> * ColorWell        @familyBluesDarkColorWell
        
        > ---
        
        > : Margins:
        > * VerticalStack
        >> [X] Show Eyes       @showMarginsCheckbox
        >> [ ] Override Color  @marginsColorCheckbox
        >> * HorizontalStack   @marginsColorStack
        >>> * ColorWell        @marginsLightColorWell
        >>> * ColorWell        @marginsDarkColorWell
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
            fontDimensionsLightColorWell=dict(
                width=colorwell_width
            ),
            fontDimensionsDarkColorWell=dict(
                width=colorwell_width
            ),
            fontDimensionsColorStack=dict(
                height=colorwell_height
            ),
            localGuidesLightColorWell=dict(
                width=colorwell_width
            ),
            localGuidesDarkColorWell=dict(
                width=colorwell_width
            ),
            localGuidesColorStack=dict(
                height=colorwell_height
            ),
            globalGuidesLightColorWell=dict(
                width=colorwell_width
            ),
            globalGuidesDarkColorWell=dict(
                width=colorwell_width
            ),
            globalGuidesColorStack=dict(
                height=colorwell_height
            ),
            bluesLightColorWell=dict(
                width=colorwell_width
            ),
            bluesDarkColorWell=dict(
                width=colorwell_width
            ),
            bluesColorStack=dict(
                height=colorwell_height
            ),
            familyBluesLightColorWell=dict(
                width=colorwell_width
            ),
            familyBluesDarkColorWell=dict(
                width=colorwell_width
            ),
            familyBluesColorStack=dict(
                height=colorwell_height
            ),
            marginsLightColorWell=dict(
                width=colorwell_width
            ),
            marginsDarkColorWell=dict(
                width=colorwell_width
            ),
            marginsColorStack=dict(
                height=colorwell_height
            ),
        )
        self.w = ezui.EZWindow(
            title="Eyeliner Settings",
            content=content,
            descriptionData=descriptionData,
            controller=self
        )
        # Update enable/disable color wells with their corresponding checkboxes
        for item_name in self.w.getItem("form2").getItems():
            print(item_name)
            if "ColorWell" in item_name:
                self.w.getItem(item_name).set(DEFAULT_COLORS["eyeliner_" + item_name.replace("Well", "")])
        self.contentCallback(None)

    def started(self):
        self.w.open()

    def showEyesCheckboxCallback(self, sender):
        for item_name in self.w.getItem("form2").getItems():
            self.w.getItem(item_name).enable(sender.get())
            
    def contentCallback(self, sender):
        # Update enable/disable color wells with their corresponding checkboxes
        for item_name in self.w.getItem("form2").getItems():
            print(item_name)
            if "ColorWell" in item_name:
                checkbox_name = item_name.replace("ColorWell", "Checkbox").replace("Light", "Color").replace("Dark", "Color")
                checkbox = self.w.getItem(checkbox_name)
                # checkbox.setTitle(["Override Color", ""][checkbox.get()])
                self.w.getItem(item_name).enable(checkbox.get())

DemoController()