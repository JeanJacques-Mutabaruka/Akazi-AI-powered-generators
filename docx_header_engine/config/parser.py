"""
config/parser.py
-----------------------------------------------------------
CHANGEMENTS V2 :
  ✅ resolve_vars(config, variables) — substitution récursive {{variable}}
     Parcourt TOUT le dict config avant le parse et remplace chaque
     occurrence de {{clé}} par la valeur correspondante dans `variables`.
     Fonctionne sur les strings imbriquées à n'importe quelle profondeur
     (dict, list, str) — int/float/bool passent sans modification.
"""

import re
from ..elements.factory import ElementFactory


class ConfigParser:
    """
    Parse la config YAML/dict en objets elements.

    Clés spéciales transmises par section :
      _col_widths   : [l, c, r] proportions colonnes
      _top_line     : {"thickness_pt": N, "color": "XXXXXX"}
      _bottom_line  : idem
      _distance_cm  : float distance bord de page

    _merge est géré au niveau racine du parsed dict.
    """

    SPECIAL_KEYS = {"_col_widths", "_top_line", "_bottom_line", "_distance_cm"}

    # ── Regex pour détecter {{variable}} ──────────────────────────────────
    _VAR_RE = re.compile(r"\{\{(\w+)\}\}")

    # =========================================================================
    # VARIABLE SUBSTITUTION  (nouveau)
    # =========================================================================

    @classmethod
    def resolve_vars(cls, config: dict, variables: dict) -> dict:
        """
        Parcourt récursivement `config` et remplace chaque occurrence
        de {{clé}} dans les valeurs string par variables[clé].

        Règles :
          - Clé inconnue → laissée telle quelle (pas d'erreur, pas de log)
          - Valeurs non-string (int, float, bool, None) → intactes
          - Structures dict/list → parcourues récursivement

        Args:
            config    : dict de config YAML (avant parse)
            variables : dict {nom: valeur_string}  ex: {"consultant_initials": "NKA"}

        Returns:
            Nouveau dict avec toutes les {{variable}} résolues.

        Usage :
            resolved = ConfigParser.resolve_vars(raw_yaml_dict, {
                "consultant_initials": "NKA",
                "title":              "Tech Lead Data",
                "years":              "12",
            })
            parsed = ConfigParser.parse(resolved)
        """
        if not variables:
            return config
        return cls._resolve_node(config, variables)

    @classmethod
    def _resolve_node(cls, node, variables: dict):
        """Dispatch récursif selon le type du nœud."""
        if isinstance(node, dict):
            return {k: cls._resolve_node(v, variables) for k, v in node.items()}
        if isinstance(node, list):
            return [cls._resolve_node(item, variables) for item in node]
        if isinstance(node, str):
            return cls._resolve_string(node, variables)
        # int, float, bool, None → intacts
        return node

    @classmethod
    def _resolve_string(cls, text: str, variables: dict) -> str:
        """Remplace chaque {{clé}} dans text par variables.get(clé, '{{clé}}')."""
        def replacer(match):
            key = match.group(1)
            return str(variables.get(key, match.group(0)))  # garde {{clé}} si absent
        return cls._VAR_RE.sub(replacer, text)

    # =========================================================================
    # PARSE  (inchangé)
    # =========================================================================

    @staticmethod
    def parse(config: dict) -> dict:
        """
        Convertit un dict de config (raw ou déjà résolu) en objets éléments.
        Appeler resolve_vars() EN AMONT si des variables doivent être substituées.
        """
        parsed = {}

        # _merge : paramètre racine (pas par section)
        if "_merge" in config:
            parsed["_merge"] = config["_merge"]

        for section_type in [
            "header", "footer",
            "header_first", "footer_first",
            "header_even",  "footer_even",
        ]:
            section_cfg = config.get(section_type)
            if not section_cfg:
                continue

            parsed[section_type] = {}

            # Clés spéciales : transmises telles quelles
            for key in ConfigParser.SPECIAL_KEYS:
                if key in section_cfg:
                    parsed[section_type][key] = section_cfg[key]

            # Zones : convertis en éléments, avec protection individuelle
            for zone in ["left", "center", "right"]:
                if zone not in section_cfg:
                    continue
                elements = []
                for el in (section_cfg[zone] or []):
                    if not el.get("type", ""):
                        continue
                    try:
                        elements.append(ElementFactory.create(el))
                    except Exception as e:
                        import warnings
                        warnings.warn(
                            f"[ConfigParser] élément ignoré "
                            f"({section_type}.{zone} type={el.get('type')}) : {e}"
                        )
                if elements:
                    parsed[section_type][zone] = elements

        return parsed
