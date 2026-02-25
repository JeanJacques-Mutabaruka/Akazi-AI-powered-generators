from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt


def _hex_to_rgb(hex_color: str):
    """Convertit une couleur hex (sans #) en tuple (r, g, b)."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return (0, 0, 0)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class ZoneManager:
    """
    Cree et remplit la table 3 colonnes (left / center / right) dans un header/footer.

    Nouvelles features v3:
      - _col_widths   : proportions L / C / R (ex. [2, 1, 2])
      - _top_line     : ligne horizontale AVANT le tableau (full width)
      - _bottom_line  : ligne horizontale APRES  le tableau (full width)
      - Suppression des bordures de table (invisible)
      - Support merge : conserve le contenu existant avant d'ajouter

    Note unites :
        python-docx travaille en EMU pour les marges/largeurs de page.
        Les tableaux Word (OOXML) utilisent des dxa (twips = 1/1440 inch).
        1 dxa = 635 EMU  (= 914400 EMU/inch / 1440 dxa/inch)
    """

    DEFAULT_COL_WIDTHS = [1, 1, 1]
    EMU_PER_DXA = 635

    def __init__(self, section, container, merge=False, col_widths=None,
                 top_line=None, bottom_line=None):
        self.section    = section
        self.container  = container
        self.merge      = merge
        self.col_widths = col_widths or self.DEFAULT_COL_WIDTHS
        self.top_line   = top_line    or {}
        self.bottom_line = bottom_line or {}

    def apply(self, zone_config):

        usable_emu = (
            self.section.page_width
            - self.section.left_margin
            - self.section.right_margin
        )
        usable_dxa = int(usable_emu / self.EMU_PER_DXA)

        # Vider le contenu existant (sauf si merge)
        if not self.merge:
            body = self.container._element
            for child in list(body):
                tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if tag in ("p", "tbl"):
                    body.remove(child)

        # Ligne horizontale full-width AU-DESSUS du tableau
        if self.top_line:
            self._add_full_width_line(
                thickness_pt=float(self.top_line.get("thickness_pt", 1.0)),
                color_hex=self.top_line.get("color", "000000"),
                usable_dxa=usable_dxa
            )

        # Table 3 colonnes
        table = self.container.add_table(rows=1, cols=3, width=usable_emu)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        self._set_table_widths(table, usable_dxa)
        self._remove_table_borders(table)

        # Remplir les zones
        zones = ["left", "center", "right"]
        for i, zone in enumerate(zones):
            if zone in zone_config:
                cell = table.rows[0].cells[i]
                for p in list(cell.paragraphs):
                    p._element.getparent().remove(p._element)
                for element in zone_config[zone]:
                    element.render(cell)

        # Ligne horizontale full-width EN-DESSOUS du tableau
        if self.bottom_line:
            self._add_full_width_line(
                thickness_pt=float(self.bottom_line.get("thickness_pt", 1.0)),
                color_hex=self.bottom_line.get("color", "000000"),
                usable_dxa=usable_dxa
            )

    # ------------------------------------------------------------------
    # Ligne horizontale full-width via table 1x1
    # ------------------------------------------------------------------

    def _add_full_width_line(self, thickness_pt: float, color_hex: str, usable_dxa: int):
        """
        Ajoute une ligne horizontale full-width dans le header/footer.
        Implementation : paragraphe avec bordure basse (pBdr/bottom) en dxa.
        Plus fiable que le tableau 1x1 qui peut ajouter de l'espace vertical.
        """
        # Conversion pt -> dxa pour l'epaisseur : 1pt = 20 twips, sz est en 1/8pt
        # Word utilise w:sz en huitiemes de point pour les bordures
        sz_eighths = max(1, int(thickness_pt * 8))
        color_str  = color_hex.lstrip("#").upper()

        # Creer un paragraphe avec bordure basse = la "ligne"
        p_elem = OxmlElement("w:p")

        # Style : pas d'espace avant/apres, hauteur minimale
        pPr = OxmlElement("w:pPr")

        # Espacement minimal
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:before"), "0")
        spacing.set(qn("w:after"),  "0")
        spacing.set(qn("w:line"),   "240")
        spacing.set(qn("w:lineRule"), "auto")
        pPr.append(spacing)

        # Bordure basse = la ligne visible
        pBdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"),   "single")
        bottom.set(qn("w:sz"),    str(sz_eighths))
        bottom.set(qn("w:space"), "0")
        bottom.set(qn("w:color"), color_str)
        pBdr.append(bottom)
        pPr.append(pBdr)

        # Indentation 0 pour couvrir toute la largeur
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"),  "0")
        ind.set(qn("w:right"), "0")
        pPr.append(ind)

        p_elem.append(pPr)
        # Run vide (pas de texte — la ligne est uniquement visuelle)
        r = OxmlElement("w:r")
        p_elem.append(r)

        self.container._element.append(p_elem)

    # ------------------------------------------------------------------
    # Fix largeurs : tblW + tblGrid + tcW en dxa
    # ------------------------------------------------------------------

    def _set_table_widths(self, table, usable_dxa):
        tbl   = table._tbl
        tblPr = tbl.find(qn("w:tblPr"))

        tblW = tblPr.find(qn("w:tblW"))
        if tblW is not None:
            tblW.set(qn("w:type"), "dxa")
            tblW.set(qn("w:w"),    str(usable_dxa))
        else:
            tblW = OxmlElement("w:tblW")
            tblW.set(qn("w:type"), "dxa")
            tblW.set(qn("w:w"),    str(usable_dxa))
            tblPr.insert(0, tblW)

        existing_grid = tbl.find(qn("w:tblGrid"))
        if existing_grid is not None:
            tbl.remove(existing_grid)

        total_parts    = sum(self.col_widths)
        col_widths_dxa = [int(usable_dxa * p / total_parts) for p in self.col_widths]
        col_widths_dxa[-1] += usable_dxa - sum(col_widths_dxa)

        tblGrid = OxmlElement("w:tblGrid")
        for w in col_widths_dxa:
            gridCol = OxmlElement("w:gridCol")
            gridCol.set(qn("w:w"), str(w))
            tblGrid.append(gridCol)

        tblPr_idx = list(tbl).index(tblPr)
        tbl.insert(tblPr_idx + 1, tblGrid)

        for i, cell in enumerate(table.rows[0].cells):
            tc   = cell._tc
            tcPr = tc.get_or_add_tcPr()
            tcW  = tcPr.find(qn("w:tcW"))
            if tcW is not None:
                tcPr.remove(tcW)
            tcW = OxmlElement("w:tcW")
            tcW.set(qn("w:type"), "dxa")
            tcW.set(qn("w:w"),    str(col_widths_dxa[i]))
            tcPr.insert(0, tcW)

        return col_widths_dxa

    # ------------------------------------------------------------------
    # Suppression bordures table
    # ------------------------------------------------------------------

    @staticmethod
    def _remove_table_borders(table):
        tbl   = table._tbl
        tblPr = tbl.find(qn("w:tblPr"))
        if tblPr is None:
            tblPr = OxmlElement("w:tblPr")
            tbl.insert(0, tblPr)

        existing = tblPr.find(qn("w:tblBorders"))
        if existing is not None:
            tblPr.remove(existing)

        tblBorders = OxmlElement("w:tblBorders")
        for border_name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
            border = OxmlElement(f"w:{border_name}")
            border.set(qn("w:val"),   "none")
            border.set(qn("w:sz"),    "0")
            border.set(qn("w:space"), "0")
            border.set(qn("w:color"), "auto")
            tblBorders.append(border)
        tblPr.append(tblBorders)

        for cell in table.rows[0].cells:
            tc   = cell._tc
            tcPr = tc.get_or_add_tcPr()
            existing_cb = tcPr.find(qn("w:tcBorders"))
            if existing_cb is not None:
                tcPr.remove(existing_cb)
            tcBorders = OxmlElement("w:tcBorders")
            for border_name in ["top", "left", "bottom", "right"]:
                border = OxmlElement(f"w:{border_name}")
                border.set(qn("w:val"),   "none")
                border.set(qn("w:sz"),    "0")
                border.set(qn("w:space"), "0")
                border.set(qn("w:color"), "auto")
                tcBorders.append(border)
            tcPr.append(tcBorders)
