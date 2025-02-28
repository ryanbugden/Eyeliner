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
    "marginsLightColorWell": (0,0,0,1),
    "marginsDarkColorWell": (1,1,1,1),
    "fontDimensionsLightColorWell": get_flattened_alpha(getDefault("glyphViewFontMetricsStrokeColor")),
    "fontDimensionsDarkColorWell": get_flattened_alpha(getDefault("glyphViewFontMetricsStrokeColor.dark")),
    "bluesLightColorWell": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewBluesColor"))),
    "bluesDarkColorWell": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewBluesColor.dark"))),
    "familyBluesLightColorWell": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewFamilyBluesColor"))),
    "familyBluesDarkColorWell": get_darkened_blue(get_flattened_alpha(getDefault("glyphViewFamilyBluesColor.dark"))),
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
        
        >> * HorizontalStack   @fontDimensionsLabelStack
        >>> Light Mode         @fontDimensionsLightModeLabel
        >>> Dark Mode          @fontDimensionsDarkModeLabel
        
        > ---
                
        > : Blue Zones:
        > * VerticalStack
        >> [X] Show Eyes       @showBluesCheckbox
        >> [ ] Override Color  @bluesColorCheckbox
        >> * HorizontalStack   @bluesColorStack
        >>> * ColorWell        @bluesLightColorWell
        >>> * ColorWell        @bluesDarkColorWell

        >> * HorizontalStack   @bluesLabelStack
        >>> Light Mode         @bluesLightModeLabel
        >>> Dark Mode          @bluesDarkModeLabel
        
        > ---

        > : Family Blue Zones:
        > * VerticalStack
        >> [X] Show Eyes       @showFamilyBluesCheckbox
        >> [ ] Override Color  @familyBluesColorCheckbox
        >> * HorizontalStack   @familyBluesColorStack
        >>> * ColorWell        @familyBluesLightColorWell
        >>> * ColorWell        @familyBluesDarkColorWell

        >> * HorizontalStack   @familyBluesLabelStack
        >>> Light Mode         @familyBluesLightModeLabel
        >>> Dark Mode          @familyBluesDarkModeLabel
        
        > ---
        
        > : Margins:
        > * VerticalStack
        >> [X] Show Eyes       @showMarginsCheckbox
        >> [ ] Override Color  @marginsColorCheckbox
        >> * HorizontalStack   @marginsColorStack
        >>> * ColorWell        @marginsLightColorWell
        >>> * ColorWell        @marginsDarkColorWell
        
        >> * HorizontalStack   @marginsLabelStack
        >>> Light Mode         @marginsLightModeLabel
        >>> Dark Mode          @marginsDarkModeLabel
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
            fontDimensionsLightModeLabel=dict(
                width=colorwell_width,
                sizeStyle='mini',
            ),
            fontDimensionsDarkModeLabel=dict(
                width=colorwell_width,
                sizeStyle='mini',
            ),
            bluesLightModeLabel=dict(
                width=colorwell_width,
                sizeStyle='mini',
            ),
            bluesDarkModeLabel=dict(
                width=colorwell_width,
                sizeStyle='mini',
            ),
            familyBluesLightModeLabel=dict(
                width=colorwell_width,
                sizeStyle='mini',
            ),
            familyBluesDarkModeLabel=dict(
                width=colorwell_width,
                sizeStyle='mini',
            ),
            marginsLightModeLabel=dict(
                width=colorwell_width,
                sizeStyle='mini',
            ),
            marginsDarkModeLabel=dict(
                width=colorwell_width,
                sizeStyle='mini',
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
            if "ColorWell" in item_name:
                self.w.getItem(item_name).set(DEFAULT_COLORS[item_name])
        self.contentCallback(None)

    def started(self):
        self.w.open()
            
    def contentCallback(self, sender):
        # Update enable/disable color wells with their corresponding checkboxes
        for item_name in self.w.content.getItems():
            if "ColorWell" in item_name:
                checkbox_name = item_name.replace("ColorWell", "Checkbox").replace("Light", "Color").replace("Dark", "Color")
                checkbox = self.w.getItem(checkbox_name)
                self.w.getItem(item_name).enable(checkbox.get())
                # Reset color to extension defaults
                if not checkbox.get():
                    self.w.getItem(item_name).set(DEFAULT_COLORS[item_name])
        # Hide or show everything, depending on whether Show Eyes is checked
        show_eyes = self.w.getItem("showEyesCheckbox").get()
        for item_name in self.w.getItem("form2").getItems():
            if ("show" in item_name and "Checkbox" in item_name):
                self.w.getItem(item_name).enable(show_eyes)

DemoController()