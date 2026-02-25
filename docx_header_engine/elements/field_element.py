
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from .base_element import BaseElement

class FieldElement(BaseElement):

    def __init__(self, config):
        self.value = config.get("value")

    def render(self, container):

        p = container.add_paragraph()
        run = p.add_run()

        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'begin')

        instrText = OxmlElement('w:instrText')
        instrText.text = self.value

        fldCharEnd = OxmlElement('w:fldChar')
        fldCharEnd.set(qn('w:fldCharType'), 'end')

        run._r.append(fldChar)
        run._r.append(instrText)
        run._r.append(fldCharEnd)
