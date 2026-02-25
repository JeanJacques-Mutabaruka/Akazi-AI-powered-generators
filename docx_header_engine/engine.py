from .section_manager import SectionManager
from .config.parser import ConfigParser


class HeaderFooterEngine:
    """
    Point d'entrée principal du package docx_header_engine v2.

    Usage simple (dict Python):
        engine = HeaderFooterEngine(doc)
        engine.apply(config_dict)

    Usage YAML (Feature 6):
        engine = HeaderFooterEngine(doc)
        engine.apply_yaml("header_config.yaml")

    Options:
        merge=True  →  Feature 4: conserve le contenu header existant
    """

    def __init__(self, document):
        self.document = document

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def apply(self, config, merge=False):
        """Applique un config dict au document."""
        config["_merge"] = merge
        parsed = ConfigParser.parse(config)
        self._apply_even_odd_if_needed(parsed)
        SectionManager(self.document).apply(parsed)

    def apply_yaml(self, yaml_path, merge=False):
        """Feature 6: Charge un fichier YAML et l'applique."""
        config = self._load_yaml(yaml_path)
        self.apply(config, merge=merge)

    def apply_excel(self, excel_path, merge=False):
        """Charge un fichier Excel (loader existant) et l'applique."""
        from .config.excel_loader import ExcelConfigLoader
        config = ExcelConfigLoader.load(excel_path)
        self.apply(config, merge=merge)

    # ------------------------------------------------------------------
    # Feature 6: YAML loader
    # ------------------------------------------------------------------

    @staticmethod
    def _load_yaml(yaml_path):
        """
        Charge un fichier YAML de configuration header/footer.

        Format YAML attendu:
        ---
        header:
          left:
            - type: image
              path: logo.png
              width_cm: 3.0
          right:
            - type: inline_group
              align: right
              style:
                font: Calibri
                size: 9
              items:
                - type: text
                  value: "Page "
                - type: field
                  value: " PAGE "
                - type: text
                  value: " / "
                - type: field
                  value: " NUMPAGES "
        footer:
          center:
            - type: text
              value: "Confidentiel"
              style:
                italic: true
                size: 8
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML est requis pour le support YAML. "
                "Installez-le avec: pip install pyyaml"
            )

        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    # ------------------------------------------------------------------
    # Feature 3: Activer even/odd au niveau document si nécessaire
    # ------------------------------------------------------------------

    def _apply_even_odd_if_needed(self, config):
        """
        Active w:evenAndOddHeaders dans les settings du document
        si une config even_page est détectée.
        """
        needs_even_odd = any(
            k in config for k in ("header_even", "footer_even")
        )

        if not needs_even_odd:
            return

        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        settings = self.document.settings.element
        if settings.find(qn('w:evenAndOddHeaders')) is None:
            even_odd = OxmlElement('w:evenAndOddHeaders')
            settings.append(even_odd)
