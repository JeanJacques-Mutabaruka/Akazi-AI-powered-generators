
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .base_element import BaseElement

class TextElement(BaseElement):

    def __init__(self, config):
        self.value = config.get("value", "")
        self.style = config.get("style", {})

    def render(self, container):

        p = container.add_paragraph()
        run = p.add_run(self.value)

        if "font" in self.style:
            run.font.name = self.style["font"]

        if "size" in self.style:
            run.font.size = Pt(self.style["size"])

        if "bold" in self.style:
            run.bold = self.style["bold"]

        if "italic" in self.style:
            run.italic = self.style["italic"]

        if "color" in self.style:
            run.font.color.rgb = RGBColor.from_string(self.style["color"])

        align = self.style.get("align")

        if align == "center":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif align == "right":
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
