from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm
from .zone_manager import ZoneManager


class SectionManager:
    """Applique les headers/footers sur chaque section Word."""

    def __init__(self, document):
        self.document = document

    def apply(self, config):
        for section in self.document.sections:
            self._apply_section(section, config)

    def _apply_section(self, section, config):
        has_first = bool(config.get("header_first")) or bool(config.get("footer_first"))
        has_even  = bool(config.get("header_even"))  or bool(config.get("footer_even"))

        if has_first:
            self._enable_title_page(section)
        if has_even:
            self._enable_different_even_odd(section)

        merge = config.get("_merge", False)

        if config.get("header"):
            hcfg = config["header"]
            self._apply_distance(section, "header", hcfg.get("_distance_cm"))
            ZoneManager(
                section, section.header, merge=merge,
                col_widths=hcfg.get("_col_widths"),
                top_line=hcfg.get("_top_line"),
                bottom_line=hcfg.get("_bottom_line"),
            ).apply(hcfg)

        if config.get("footer"):
            fcfg = config["footer"]
            self._apply_distance(section, "footer", fcfg.get("_distance_cm"))
            ZoneManager(
                section, section.footer, merge=merge,
                col_widths=fcfg.get("_col_widths"),
                top_line=fcfg.get("_top_line"),
                bottom_line=fcfg.get("_bottom_line"),
            ).apply(fcfg)

        if has_first:
            if config.get("header_first"):
                hfcfg = config["header_first"]
                self._apply_distance(section, "header", hfcfg.get("_distance_cm"))
                ZoneManager(section, section.first_page_header,
                            col_widths=hfcfg.get("_col_widths"),
                            top_line=hfcfg.get("_top_line"),
                            bottom_line=hfcfg.get("_bottom_line"),
                ).apply(hfcfg)
            if config.get("footer_first"):
                ffcfg = config["footer_first"]
                self._apply_distance(section, "footer", ffcfg.get("_distance_cm"))
                ZoneManager(section, section.first_page_footer,
                            col_widths=ffcfg.get("_col_widths"),
                            top_line=ffcfg.get("_top_line"),
                            bottom_line=ffcfg.get("_bottom_line"),
                ).apply(ffcfg)

        if has_even:
            if config.get("header_even"):
                hecfg = config["header_even"]
                ZoneManager(section, section.even_page_header,
                            col_widths=hecfg.get("_col_widths"),
                            top_line=hecfg.get("_top_line"),
                            bottom_line=hecfg.get("_bottom_line"),
                ).apply(hecfg)
            if config.get("footer_even"):
                fecfg = config["footer_even"]
                ZoneManager(section, section.even_page_footer,
                            col_widths=fecfg.get("_col_widths"),
                            top_line=fecfg.get("_top_line"),
                            bottom_line=fecfg.get("_bottom_line"),
                ).apply(fecfg)

    @staticmethod
    def _apply_distance(section, part: str, distance_cm):
        if distance_cm is None:
            return
        try:
            val = Cm(float(distance_cm))
            if part == "header":
                section.header_distance = val
            else:
                section.footer_distance = val
        except Exception:
            pass

    @staticmethod
    def _enable_title_page(section):
        sectPr = section._sectPr
        if sectPr.find(qn("w:titlePg")) is None:
            sectPr.append(OxmlElement("w:titlePg"))

    @staticmethod
    def _enable_different_even_odd(section):
        sectPr = section._sectPr
        if sectPr.find(qn("w:evenAndOddHeaders")) is None:
            sectPr.append(OxmlElement("w:evenAndOddHeaders"))
