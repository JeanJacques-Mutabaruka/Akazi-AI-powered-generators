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

    @staticmethod
    def parse(config):
        parsed = {}

        # _merge : paramètre racine (pas par section)
        if "_merge" in config:
            parsed["_merge"] = config["_merge"]

        for section_type in ["header", "footer",
                              "header_first", "footer_first",
                              "header_even",  "footer_even"]:
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
