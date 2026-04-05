"""
docx_header_engine/engine.py
-----------------------------------------------------------
CHANGEMENTS V2 :
  ✅ apply_yaml_with_vars(yaml_path, variables, merge) — nouvelle API publique
     Charge le YAML, résout les {{variables}} depuis le dict fourni,
     puis applique au document. Zéro impact sur apply() / apply_yaml() existants.
"""

from .section_manager import SectionManager
from .config.parser import ConfigParser


class HeaderFooterEngine:
    """
    Point d'entrée principal du package docx_header_engine.

    Usage simple (dict Python) :
        engine = HeaderFooterEngine(doc)
        engine.apply(config_dict)

    Usage YAML statique :
        engine = HeaderFooterEngine(doc)
        engine.apply_yaml("header_config.yaml")

    Usage YAML avec variables dynamiques (nouveau) :
        engine = HeaderFooterEngine(doc)
        engine.apply_yaml_with_vars(
            "hf_presets/combined/mc2i_cv_complet.yaml",
            variables={
                "consultant_initials": "NKA",
                "title":              "Tech Lead Data",
                "years":              "12",
            }
        )

    Options :
        merge=True  →  conserve le contenu header existant avant d'ajouter
    """

    def __init__(self, document):
        self.document = document

    # =========================================================================
    # API PUBLIQUE
    # =========================================================================

    def apply(self, config: dict, merge: bool = False):
        """Applique un config dict au document."""
        config["_merge"] = merge
        parsed = ConfigParser.parse(config)
        self._apply_even_odd_if_needed(parsed)
        SectionManager(self.document).apply(parsed)

    def apply_yaml(self, yaml_path: str, merge: bool = False):
        """Charge un fichier YAML statique et l'applique."""
        config = self._load_yaml(yaml_path)
        self.apply(config, merge=merge)

    def apply_yaml_with_vars(
        self,
        yaml_path: str,
        variables: dict,
        merge: bool = False,
    ):
        """
        Charge un fichier YAML, résout les {{variables}}, puis applique.

        Les placeholders {{clé}} dans les valeurs string du YAML sont remplacés
        par variables[clé] avant le rendu.  Clés absentes → laissées intactes.

        Args:
            yaml_path : Chemin vers le fichier YAML de preset
            variables : Dict {nom: valeur_string} issu des données du JSON
                        ex: {"consultant_initials": "NKA",
                             "title": "Tech Lead Data",
                             "years": "12"}
            merge     : True → conserve le contenu header/footer existant
        """
        raw_config              = self._load_yaml(yaml_path)
        resolved_config         = ConfigParser.resolve_vars(raw_config, variables)
        resolved_config["_merge"] = merge
        parsed                  = ConfigParser.parse(resolved_config)
        self._apply_even_odd_if_needed(parsed)
        SectionManager(self.document).apply(parsed)

    def apply_excel(self, excel_path: str, merge: bool = False):
        """Charge un fichier Excel (loader existant) et l'applique."""
        from .config.excel_loader import ExcelConfigLoader
        config = ExcelConfigLoader.load(excel_path)
        self.apply(config, merge=merge)

    # =========================================================================
    # YAML LOADER  (inchangé)
    # =========================================================================

    @staticmethod
    def _load_yaml(yaml_path: str) -> dict:
        """Charge un fichier YAML de configuration header/footer."""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML est requis pour le support YAML. "
                "Installez-le avec : pip install pyyaml"
            )
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # =========================================================================
    # EVEN/ODD  (inchangé)
    # =========================================================================

    def _apply_even_odd_if_needed(self, config: dict):
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
        if settings.find(qn("w:evenAndOddHeaders")) is None:
            even_odd = OxmlElement("w:evenAndOddHeaders")
            settings.append(even_odd)
