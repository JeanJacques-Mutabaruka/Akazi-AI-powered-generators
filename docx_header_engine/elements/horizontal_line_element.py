
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from .base_element import BaseElement

class HorizontalLineElement(BaseElement):

    def __init__(self, config):
        self.thickness = config.get("thickness_pt", 1)
        self.color = config.get("color", "000000")

    def render(self, container):
        p = container.add_paragraph()
        p_format = p.paragraph_format
        p_format.space_before = Pt(2)
        p_format.space_after = Pt(2)

        pPr = p._p.get_or_add_pPr()
        border = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), str(int(self.thickness * 8)))
        bottom.set(qn("w:color"), self.color)

        border.append(bottom)
        pPr.append(border)
