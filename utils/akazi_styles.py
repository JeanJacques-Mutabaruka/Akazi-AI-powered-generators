"""
akazi_styles.py
-----------------------------------------
Style manager centralisé pour tous les documents AKAZI

- Création des styles personnalisés
- Gestion visibilité galerie Word
- Suppression contextual spacing
- Hiérarchie UI propre
- Stable python-docx 0.8.x
"""

from docx.shared import Pt, Cm
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class AkaziStyleManager:

    FONT_NAME = "Century Gothic"

    def __init__(self, document):
        self.doc = document
        self.styles = self.doc.styles

    # ==========================================================
    # PUBLIC ENTRY POINT
    # ==========================================================

    def setup_all_styles(self):
        self._create_section_title_style()
        self._create_normal_paragraph_style()
        self._create_bullet_level1_style()
        self._create_bullet_level2_style()
        self._create_akazi_numbering()


    # ==========================================================
    # STYLE CREATION
    # ==========================================================

    def _create_section_title_style(self):
        name = "Akazi Section Title"

        if name in self.styles:
            return

        style = self.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)

        style.font.name = self.FONT_NAME
        style.font.size = Pt(12)
        style.font.bold = True

        pf = style.paragraph_format
        pf.space_before = Pt(20)
        pf.space_after = Pt(6)
        pf.left_indent = Cm(0)
        pf.first_line_indent = Cm(0)
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = 1.15

        self._finalize_style(style, priority=1)

    # ----------------------------------------------------------

    def _create_normal_paragraph_style(self):
        name = "Akazi Normal"

        if name in self.styles:
            return

        style = self.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)

        style.font.name = self.FONT_NAME
        style.font.size = Pt(10)

        pf = style.paragraph_format
        pf.space_before = Pt(3)
        pf.space_after = Pt(3)
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = 1.15

        self._finalize_style(style, priority=2)

    # ----------------------------------------------------------

    def _create_bullet_level1_style(self):
        name = "Akazi Bullet Level 1"

        if name in self.styles:
            return

        style = self.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = self.styles["List Paragraph"]

        style.font.name = self.FONT_NAME
        style.font.size = Pt(10)

        pf = style.paragraph_format
        pf.left_indent = Cm(1.0)
        pf.first_line_indent = Cm(-0.5)
        pf.space_before = Pt(3)
        pf.space_after = Pt(3)
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = 1.15

        self._finalize_style(style, priority=3)

    # ----------------------------------------------------------

    def _create_bullet_level2_style(self):
        name = "Akazi Bullet Level 2"

        if name in self.styles:
            return

        style = self.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = self.styles["List Paragraph"]

        style.font.name = self.FONT_NAME
        style.font.size = Pt(10)

        pf = style.paragraph_format
        pf.left_indent = Cm(1.5)
        pf.first_line_indent = Cm(-0.5)
        pf.space_before = Pt(3)
        pf.space_after = Pt(3)
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = 1.15

        self._finalize_style(style, priority=4)

    # ==========================================================
    # INTERNAL UTILITIES
    # ==========================================================

    def _finalize_style(self, style, priority: int):
        """
        - Rend le style visible dans la galerie
        - Supprime contextual spacing
        - Définit priorité UI
        """

        style_element = style.element

        # ---- Supprimer contextualSpacing ----
        pPr = style_element.get_or_add_pPr()
        contextual = pPr.find(qn("w:contextualSpacing"))
        if contextual is not None:
            pPr.remove(contextual)

        # ---- qFormat (style recommandé) ----
        qformat = OxmlElement("w:qFormat")
        style_element.append(qformat)

        # ---- uiPriority ----
        priority_el = OxmlElement("w:uiPriority")
        priority_el.set(qn("w:val"), str(priority))
        style_element.append(priority_el)

        # ---- unhideWhenUsed ----
        unhide = OxmlElement("w:unhideWhenUsed")
        style_element.append(unhide)

        # ---- retirer semiHidden si présent ----
        semi_hidden = style_element.find(qn("w:semiHidden"))
        if semi_hidden is not None:
            style_element.remove(semi_hidden)

    @staticmethod
    def apply_bullet(paragraph, level=0):
        """
        Applique la numérotation AKAZI custom
        """

        p = paragraph._p
        pPr = p.get_or_add_pPr()

        numPr = OxmlElement('w:numPr')

        ilvl = OxmlElement('w:ilvl')
        ilvl.set(qn('w:val'), str(level))
        numPr.append(ilvl)

        numId = OxmlElement('w:numId')
        numId.set(qn('w:val'), '99')  # notre numérotation custom
        numPr.append(numId)

        pPr.append(numPr)


    def _create_akazi_numbering(self):
        """
        Crée une numérotation custom AKAZI :
        Level 0 = ●
        Level 1 = °
        """

        numbering = self.doc.part.numbering_part.numbering_definitions._numbering

        abstract_num = OxmlElement('w:abstractNum')
        abstract_num.set(qn('w:abstractNumId'), '99')

        # ============ LEVEL 0 (●) ============
        lvl0 = OxmlElement('w:lvl')
        lvl0.set(qn('w:ilvl'), '0')

        numFmt = OxmlElement('w:numFmt')
        numFmt.set(qn('w:val'), 'bullet')
        lvl0.append(numFmt)

        lvlText = OxmlElement('w:lvlText')
        lvlText.set(qn('w:val'), '•')
        lvl0.append(lvlText)

        abstract_num.append(lvl0)

        # ============ LEVEL 1 (°) ============
        lvl1 = OxmlElement('w:lvl')
        lvl1.set(qn('w:ilvl'), '1')

        numFmt1 = OxmlElement('w:numFmt')
        numFmt1.set(qn('w:val'), 'bullet')
        lvl1.append(numFmt1)

        lvlText1 = OxmlElement('w:lvlText')
        lvlText1.set(qn('w:val'), '°')
        lvl1.append(lvlText1)

        abstract_num.append(lvl1)

        numbering.append(abstract_num)

        # Lier numId à abstractNum
        num = OxmlElement('w:num')
        num.set(qn('w:numId'), '99')

        abstractNumId = OxmlElement('w:abstractNumId')
        abstractNumId.set(qn('w:val'), '99')

        num.append(abstractNumId)
        numbering.append(num)
