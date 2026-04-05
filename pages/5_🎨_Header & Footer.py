"""
Page 5 — Header & Footer V9
NOUVEAUTÉS V9 :
  ✅ UI Versioning : uk(base) génère des keys versionnées → chargement preset
     fiable sans liste de purge. Incrémenter _ui_version suffit pour que
     tous les widgets relisent leurs valeurs depuis hf_config.
  ✅ deepcopy systématique sur toutes les écritures dans hf_config
  ✅ Preview HTML live : aperçu visuel header/footer dans l'éditeur
  ✅ _purge_element_keys supprimée (remplacée par le versioning)
  ✅ _apply_pending_sync allégée : incrémente juste _ui_version
"""

import streamlit as st
import streamlit.components.v1 as components
import yaml
import copy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hf_preset_manager import (
    list_presets, get_preset_options, load_preset, save_preset,
    delete_preset, duplicate_preset,
    save_uploaded_image, list_available_images, get_image_options,
    TEMPLATES, ensure_dirs
)

st.set_page_config(page_title="Header & Footer", page_icon="🎨", layout="wide")

# ── Polices Word-safe ──────────────────────────────────────────────────────
FONT_LIST = [
    "Calibri", "Calibri Light", "Arial", "Arial Narrow", "Verdana",
    "Helvetica", "Tahoma", "Trebuchet MS", "Georgia", "Times New Roman",
    "Garamond", "Book Antiqua", "Palatino Linotype", "Cambria",
    "Century Gothic", "Franklin Gothic Medium", "Gill Sans MT",
    "Autre…",
]

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .tag { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
    .tag-combined { background: #e8eaf6; color: #3949ab; }
    .tag-header   { background: #fce4ec; color: #c62828; }
    .tag-footer   { background: #e8f5e9; color: #2e7d32; }
    .yaml-preview {
        background: #1e1e2e; color: #cdd6f4;
        border-radius: 8px; padding: 16px;
        font-family: 'Fira Code', 'Consolas', monospace;
        font-size: 12px; line-height: 1.6;
        max-height: 500px; overflow-y: auto;
    }
    /* ── Tabs : grands, colorés ──────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 700;
        font-size: 30px;
        padding: 14px 48px;
        border-radius: 8px 8px 0 0;
        color: #888 !important;
        background: #D9D9D9 !important;
        border-bottom: 3px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #2e7d32 !important;
        background: #e8f5e9 !important;
        border-bottom: 3px solid #43a047 !important;
    }
    .options-box {
        background: #f8f9ff; border-radius: 8px; padding: 14px 16px;
        border: 1px solid #e0e4ff; margin-bottom: 10px;
    }
    .line-preview {
        border: none; border-top: 2px solid #667eea;
        margin: 6px 0 10px; opacity: 0.5;
    }
    .preset-active {
        background: linear-gradient(90deg, #e8f5e9 0%, #f1f8e9 100%);
        border: 2px solid #43a047 !important; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

ensure_dirs()


# ── SESSION STATE ─────────────────────────────────────────────────────────

UI_VERSION_KEY = "_ui_version"   # Incrément qui invalide tous les widgets

def init_state():
    if "hf_config" not in st.session_state:
        st.session_state.hf_config = copy.deepcopy(TEMPLATES["AKAZI Standard"])
    if UI_VERSION_KEY not in st.session_state:
        st.session_state[UI_VERSION_KEY] = 0
    if "active_preset_name" not in st.session_state:
        st.session_state["active_preset_name"] = None

init_state()


def uk(base: str) -> str:
    """
    Génère une key de widget versionnée : f"{base}_v{_ui_version}".

    Quand _ui_version est incrémenté (via bump_ui()), toutes les keys
    changent. Streamlit ne trouve plus de valeur en cache pour ces nouvelles
    keys → il relit value=/index= depuis hf_config.
    C'est le remplacement définitif de _purge_element_keys().
    """
    return f"{base}_v{st.session_state[UI_VERSION_KEY]}"


def bump_ui():
    """Incrémente _ui_version → invalide tous les widgets au prochain rendu."""
    st.session_state[UI_VERSION_KEY] += 1


def set_config(cfg: dict):
    """Écrit dans hf_config avec deepcopy + invalide les widgets."""
    st.session_state.hf_config = copy.deepcopy(cfg)
    bump_ui()


# ═════════════════════════════════════════════════════════════════════════
# SYNCHRONISATION session_state widgets ← hf_config (après chargement preset)
# ═════════════════════════════════════════════════════════════════════════

def _sync_section_options_to_state():
    """
    Déclenche bump_ui() au prochain rendu via flag.
    Conservé pour compatibilité avec les appels existants.
    """
    st.session_state["_pending_options_sync"] = True


def _apply_pending_sync():
    """
    V9 : se contente de bump_ui() si le flag est positionné.
    Plus besoin de re-setter manuellement chaque key de widget :
    le versioning via uk() s'en charge automatiquement.
    """
    if not st.session_state.get("_pending_options_sync"):
        return
    st.session_state["_pending_options_sync"] = False
    bump_ui()


# ═════════════════════════════════════════════════════════════════════════
# HELPERS — accès direct session_state
# ═════════════════════════════════════════════════════════════════════════

def _cfg():
    return st.session_state.hf_config

def _get_zone(part: str, zone: str) -> list:
    return _cfg().get(part, {}).get(zone, [])

def _set_zone(part: str, zone: str, elements: list):
    if part not in _cfg():
        _cfg()[part] = {}
    _cfg()[part][zone] = elements

def _add_element(part: str, zone: str):
    elems = _get_zone(part, zone)
    elems.append({"type": "", "value": ""})
    _set_zone(part, zone, elems)

def _delete_element(part: str, zone: str, idx: int):
    elems = _get_zone(part, zone)
    if 0 <= idx < len(elems):
        elems.pop(idx)
    _set_zone(part, zone, elems)

def _update_element(part: str, zone: str, idx: int, elem: dict):
    elems = _get_zone(part, zone)
    if 0 <= idx < len(elems):
        elems[idx] = elem
    _set_zone(part, zone, elems)

def _move_element(part: str, zone: str, idx: int, direction: int):
    """Déplace l'élément idx de 'direction' positions (+1 bas, -1 haut)."""
    elems = _get_zone(part, zone)
    new_idx = idx + direction
    if 0 <= new_idx < len(elems):
        elems[idx], elems[new_idx] = elems[new_idx], elems[idx]
    _set_zone(part, zone, elems)


def _font_selector(label: str, current: str, key: str) -> str:
    """Selectbox police + champ libre si 'Autre…' choisi.
    key doit déjà être versionnée via uk() par l'appelant.
    """
    if current in FONT_LIST:
        idx = FONT_LIST.index(current)
    else:
        idx = FONT_LIST.index("Autre…")

    sel = st.selectbox(label, FONT_LIST, index=idx, key=key)
    if sel == "Autre…":
        return st.text_input("Police (saisie libre)", value=current if current not in FONT_LIST else "", key=f"{key}_custom")
    return sel

def _ensure_zones():
    """S'assure que header/footer et leurs 3 zones existent dans la config."""
    for part in ["header", "footer"]:
        if part not in _cfg():
            _cfg()[part] = {}
        for zone in ["left", "center", "right"]:
            if zone not in _cfg()[part]:
                _cfg()[part][zone] = []

def _ensure_first_page_zones():
    """S'assure que header_first/footer_first et leurs 3 zones existent."""
    for part in ["header_first", "footer_first"]:
        if part not in _cfg():
            _cfg()[part] = {}
        for zone in ["left", "center", "right"]:
            if zone not in _cfg()[part]:
                _cfg()[part][zone] = []

# ── Variables disponibles pour les presets ────────────────────────────────
# Ces variables sont résolues depuis le JSON du document au moment de la génération.
# Elles correspondent aux clés injectées par _build_hf_variables() dans mc2i_cv_generator.py
# et peuvent être étendues dans d'autres générateurs.
VARIABLES_HELP = {
    "Consultant": {
        "{{consultant_initials}}":    "Initiales du consultant  (ex: NKA)",
        "{{consultant_name}}":        "Nom complet du consultant  (ex: JEAN DUPONT)",
        "{{consultant_email}}":       "Email du consultant  (ex: j.dupont@mc2i.fr)",
        "{{years_experience}}":       "Années d'expérience calculées  (ex: 12)",
        "{{main_domain_expertise}}":  "Domaine principal d'expertise  (ex: Big Data et Cloud)",
    },
    "Document": {
        "{{format_code}}":    "Code format du document  (ex: MC2I_V1)",
        "{{language_iso}}":   "Langue du document  (ex: FRA)",
        "{{document_type}}":  "Type de document  (ex: cv)",
        "{{generated_at}}":   "Date de génération  (ex: 2026-04-01)",
    },
    "Agence": {
        "{{agency_representative}}":       "Nom du représentant agence  (ex: BENJAMIN DUPUY)",
        "{{agency_representative_email}}": "Email du représentant agence  (ex: benjamin.dupuy@mc2i.fr)",
        "{{agency_address}}":              "Adresse complète de l'agence",
    },
}


# ═════════════════════════════════════════════════════════════════════════
# TYPES D'ÉLÉMENTS
# ═════════════════════════════════════════════════════════════════════════

ELEMENT_TYPES = ["", "text", "image", "field", "inline_group", "horizontal_line", "floating_image"]
ELEMENT_TYPE_LABELS = {
    "":               "— (vide) —",
    "text":           "Texte",
    "image":          "Image",
    "field":          "Champ Word (PAGE, DATE…)",
    "inline_group":   "Groupe inline (pagination…)",
    "horizontal_line":"Ligne horizontale",
    "floating_image": "Image flottante",
}


# ═════════════════════════════════════════════════════════════════════════
# ÉDITEUR D'ÉLÉMENT
# ═════════════════════════════════════════════════════════════════════════

def _render_element_editor(elem: dict, part: str, zone: str, idx: int) -> dict:
    elem  = copy.deepcopy(elem)
    kp    = f"{part}_{zone}_{idx}"
    tlabels = [ELEMENT_TYPE_LABELS.get(t, t) for t in ELEMENT_TYPES]
    cur_l   = ELEMENT_TYPE_LABELS.get(elem.get("type", ""), "— (vide) —")

    sel_label = st.selectbox(
        "Type d'élément", tlabels,
        index=tlabels.index(cur_l) if cur_l in tlabels else 0,
        key=uk(f"{kp}_type")
    )
    etype = next((t for t, l in ELEMENT_TYPE_LABELS.items() if l == sel_label), "")
    elem["type"] = etype

    if etype == "":
        st.caption("Élément vide — non inclus dans le YAML final.")
        return elem

    if etype == "text":
        elem["value"] = st.text_area(
            "Texte (↵ pour retour à la ligne)",
            value=elem.get("value", ""),
            key=uk(f"{kp}_val"),
            height=80,
            help="Utilisez Entrée pour un retour à la ligne. "
                 "Les {{variables}} sont supportées (ex: {{consultant_initials}})."
        )
        style = elem.get("style", {})
        # Ligne 1 : Police (large) + Taille
        c1, c2 = st.columns([3, 1])
        with c1: style["font"] = _font_selector("Police", style.get("font", "Calibri"), uk(f"{kp}_font"))
        style["size"] = c2.number_input("Taille", value=int(style.get("size", 9)), min_value=6, max_value=36, key=uk(f"{kp}_size"))
        # Ligne 2 : Alignement + Gras + Couleur hex
        align_opts = ["left", "center", "right"]
        ca, cb, cc = st.columns([2, 1, 2])
        style["align"] = ca.selectbox("Alignement", align_opts, index=align_opts.index(style.get("align", "left")), key=uk(f"{kp}_align"))
        with cb:
            st.markdown("<br>", unsafe_allow_html=True)
            style["bold"] = st.checkbox("Gras", value=bool(style.get("bold", False)), key=uk(f"{kp}_bold"))
        style["color"] = cc.text_input("Couleur hex", value=style.get("color", "000000"), key=uk(f"{kp}_color"))
        elem["style"] = {k: v for k, v in style.items() if v not in [None, ""] or k == "bold"}

    elif etype == "image":
        img_opts = get_image_options()
        cur_path = elem.get("path", "")
        cur_il = next((l for l, p in img_opts.items() if p == cur_path), list(img_opts.keys())[0])
        elem["path"] = img_opts[st.selectbox("Image", list(img_opts.keys()), index=list(img_opts.keys()).index(cur_il), key=uk(f"{kp}_imgpath"))]
        c1, c2 = st.columns(2)
        elem["width_cm"] = c1.number_input("Largeur (cm)", value=float(elem.get("width_cm", 3.0)), min_value=0.5, max_value=20.0, step=0.1, key=uk(f"{kp}_w"))
        h = c2.number_input("Hauteur (cm) — 0 = auto", value=float(elem.get("height_cm", 0.0)), min_value=0.0, max_value=20.0, step=0.1, key=uk(f"{kp}_h"))
        if h > 0: elem["height_cm"] = h
        elif "height_cm" in elem: del elem["height_cm"]

    elif etype == "floating_image":
        img_opts = get_image_options()
        cur_path = elem.get("path", "")
        cur_il = next((l for l, p in img_opts.items() if p == cur_path), list(img_opts.keys())[0])
        elem["path"] = img_opts[st.selectbox("Image", list(img_opts.keys()), index=list(img_opts.keys()).index(cur_il), key=uk(f"{kp}_fimgpath"))]
        c1, c2, c3, c4 = st.columns(4)
        elem["width_cm"]  = c1.number_input("Largeur (cm)", value=float(elem.get("width_cm", 3.0)), min_value=0.5, max_value=20.0, step=0.1, key=uk(f"{kp}_fw"))
        elem["height_cm"] = c2.number_input("Hauteur (cm)", value=float(elem.get("height_cm", 1.5)), min_value=0.5, max_value=20.0, step=0.1, key=uk(f"{kp}_fh"))
        elem["x_cm"]      = c3.number_input("Position X (cm)", value=float(elem.get("x_cm", 0.0)), min_value=0.0, max_value=30.0, step=0.1, key=uk(f"{kp}_fx"))
        elem["y_cm"]      = c4.number_input("Position Y (cm)", value=float(elem.get("y_cm", 0.0)), min_value=-30.0, max_value=30.0, step=0.1, key=uk(f"{kp}_fy"))
        wrap_opts = ["none", "tight", "square"]
        elem["wrap"] = st.selectbox("Wrapping", wrap_opts, index=wrap_opts.index(elem.get("wrap", "none")), key=uk(f"{kp}_wrap"))
        elem["behind_text"] = st.checkbox(
            "🔙 Derrière le texte",
            value=bool(elem.get("behind_text", False)),
            key=uk(f"{kp}_behind"),
            help="Si coché, l'image est rendue en arrière-plan (derrière le texte). "
                 "Utile pour les images décoratives en footer (ex: motif de points MC2I)."
        )
        field_map = {" PAGE ": "Numéro de page", " NUMPAGES ": "Total pages", " DATE ": "Date", " TIME ": "Heure", " TITLE ": "Titre du document"}
        rev_map   = {v: k for k, v in field_map.items()}
        cur_fl    = field_map.get(elem.get("value", " PAGE "), "Numéro de page")
        elem["value"] = rev_map[st.selectbox("Champ Word", list(field_map.values()), index=list(field_map.values()).index(cur_fl), key=uk(f"{kp}_field"))]

    elif etype == "horizontal_line":
        c1, c2 = st.columns(2)
        elem["thickness_pt"] = c1.number_input("Épaisseur (pt)", value=int(elem.get("thickness_pt", 1)), min_value=1, max_value=10, key=uk(f"{kp}_thick"))
        elem["color"]        = c2.text_input("Couleur hex", value=elem.get("color", "000000"), key=uk(f"{kp}_lcolor"))

    elif etype == "inline_group":
        align_opts = ["left", "center", "right"]
        elem["align"] = st.selectbox("Alignement du groupe", align_opts, index=align_opts.index(elem.get("align", "right")), key=uk(f"{kp}_galign"))
        style = elem.get("style", {})
        c1, c2, c3 = st.columns(3)
        with c1: style["font"] = _font_selector("Police", style.get("font", "Calibri"), uk(f"{kp}_gfont"))
        style["size"]  = c2.number_input("Taille", value=int(style.get("size", 9)), min_value=6, max_value=36, key=uk(f"{kp}_gsize"))
        style["color"] = c3.text_input("Couleur hex", value=style.get("color", "808080"), key=uk(f"{kp}_gcolor"))
        elem["style"]  = style
        st.markdown("**Items du groupe** *(textes + champs sur une ligne)* :")
        items     = elem.get("items", [])
        new_items = []
        for i, item in enumerate(items):
            ci1, ci2, ci3 = st.columns([2, 4, 1])
            itype = ci1.selectbox("", ["text", "field"], index=0 if item.get("type") == "text" else 1, key=uk(f"{kp}_it{i}_type"), label_visibility="collapsed")
            ival  = ci2.text_input("", value=item.get("value", ""), key=uk(f"{kp}_it{i}_val"), label_visibility="collapsed")
            new_items.append({"type": itype, "value": ival})
            if ci3.button("✕", key=uk(f"{kp}_it{i}_del"), help="Supprimer"):
                new_items.pop()
                elem["items"] = new_items
                _update_element(part, zone, idx, elem)
                st.rerun()
        if st.button("➕ Ajouter un item", key=uk(f"{kp}_additem")):
            new_items.append({"type": "text", "value": ""})
            elem["items"] = new_items
            _update_element(part, zone, idx, elem)
            st.rerun()
        elem["items"] = new_items

    return elem


# ═════════════════════════════════════════════════════════════════════════
# ÉDITEUR DE ZONE
# ═════════════════════════════════════════════════════════════════════════

ZONE_STYLES = {
    "header": {
        "left":   {"icon": "🟥", "color": "#c62828", "border": "#e57373"},
        "center": {"icon": "🟨", "color": "#f57f17", "border": "#ffd54f"},
        "right":  {"icon": "🟦", "color": "#1565c0", "border": "#64b5f6"},
    },
    "footer": {
        "left":   {"icon": "🟥", "color": "#2e7d32", "border": "#81c784"},
        "center": {"icon": "🟨", "color": "#f57f17", "border": "#ffd54f"},
        "right":  {"icon": "🟦", "color": "#1565c0", "border": "#64b5f6"},
    },
}

def _render_zone_editor(part: str, zone: str):
    style     = ZONE_STYLES.get(part, {}).get(zone, {})
    icon      = style.get("icon", "")
    color     = style.get("color", "#333")
    border    = style.get("border", "#ccc")
    zone_name = {"left": "Gauche", "center": "Centre", "right": "Droite"}.get(zone, zone)

    st.markdown(
        f"<div style='padding:8px 12px; border-left:4px solid {border}; "
        f"background:#fafafa; border-radius:6px; margin-bottom:8px;'>"
        f"<strong style='color:{color};'>{icon} {zone_name}</strong></div>",
        unsafe_allow_html=True
    )
    elements = _get_zone(part, zone)
    n = len(elements)
    for i, elem in enumerate(elements):
        etype = elem.get("type", "")
        label = ELEMENT_TYPE_LABELS.get(etype, etype) if etype else "— (vide) —"
        with st.expander(f"Élément {i+1} : `{label}`", expanded=True):
            updated = _render_element_editor(elem, part, zone, i)
            _, cb_del = st.columns([11, 1])
            with cb_del:
                if st.button("🗑️", key=uk(f"del_{part}_{zone}_{i}"),
                             help="Supprimer", use_container_width=True):
                    _delete_element(part, zone, i)
                    st.rerun()
            _update_element(part, zone, i, updated)
    if st.button(f"＋ Ajouter dans {zone_name}", key=uk(f"add_{part}_{zone}"), use_container_width=True):
        _add_element(part, zone)
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════
# OPTIONS AVANCÉES PAR SECTION (col_widths, marges, lignes full-width)
# ═════════════════════════════════════════════════════════════════════════

def _render_section_options(part: str):
    """
    Options avancées pour une section header ou footer.
    V6 : restructurées en 3 colonnes [5, 3, 2] pour gagner de l'espace.
    """
    cfg_part = _cfg().get(part, {})

    kp = f"opts_{part}"

    show_opts = st.toggle(
        f"⚙️ Options avancées ({part.upper()})",
        value=False,
        key=uk(f"{kp}_toggle")
    )

    if not show_opts:
        return

    st.markdown("---")

    # ── 3 colonnes : Largeurs | Lignes horizontales | Distance ────────────
    col_opts_l, col_opts_m, col_opts_r = st.columns([5, 3, 2])

    # ── Colonne 1 : Largeurs de colonnes ──────────────────────────────────
    with col_opts_l:
        st.markdown("**📐 Largeurs de colonnes** *(proportions relatives L / C / R)*")
        col_widths = cfg_part.get("_col_widths", [1, 1, 1])
        while len(col_widths) < 3:
            col_widths.append(1)

        cw1, cw2, cw3, cw4 = st.columns([2, 2, 2, 3])
        w_left   = cw1.number_input("Gauche",  value=float(col_widths[0]), min_value=0.1, max_value=10.0, step=0.5, key=uk(f"{kp}_cl"))
        w_center = cw2.number_input("Centre",  value=float(col_widths[1]), min_value=0.1, max_value=10.0, step=0.5, key=uk(f"{kp}_cc"))
        w_right  = cw3.number_input("Droite",  value=float(col_widths[2]), min_value=0.1, max_value=10.0, step=0.5, key=uk(f"{kp}_cr"))
        total = w_left + w_center + w_right
        with cw4:
            pct_l = int(round(w_left   / total * 100))
            pct_c = int(round(w_center / total * 100))
            pct_r = 100 - pct_l - pct_c
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption(f"→ {pct_l}% / {pct_c}% / {pct_r}%")
        _cfg()[part]["_col_widths"] = [round(w_left, 2), round(w_center, 2), round(w_right, 2)]

    # ── Colonne 2 : Lignes horizontales ───────────────────────────────────
    with col_opts_m:
        st.markdown("**─ Lignes horizontales** *(pleine largeur)*")

        top_line   = cfg_part.get("_top_line", {})
        enable_top = st.checkbox("↑ Au-dessus", value=bool(top_line), key=uk(f"{kp}_top_on"))
        if enable_top:
            lt1, lt2 = st.columns(2)
            top_thick = lt1.number_input("Épaisseur (pt)", value=float(top_line.get("thickness_pt", 1.0)),
                                          min_value=0.25, max_value=10.0, step=0.25, key=uk(f"{kp}_top_thick"))
            top_color = lt2.text_input("Couleur hex", value=top_line.get("color", "000000"), key=uk(f"{kp}_top_color"))
            _cfg()[part]["_top_line"] = {"thickness_pt": top_thick, "color": top_color}
            st.markdown(f"<hr class='line-preview' style='border-color:#{top_color}; border-top-width:{top_thick}pt;'>",
                        unsafe_allow_html=True)
        else:
            _cfg()[part].pop("_top_line", None)

        st.markdown("<br>", unsafe_allow_html=True)

        bot_line   = cfg_part.get("_bottom_line", {})
        enable_bot = st.checkbox("↓ En-dessous", value=bool(bot_line), key=uk(f"{kp}_bot_on"))
        if enable_bot:
            lb1, lb2 = st.columns(2)
            bot_thick = lb1.number_input("Épaisseur (pt)", value=float(bot_line.get("thickness_pt", 1.0)),
                                          min_value=0.25, max_value=10.0, step=0.25, key=uk(f"{kp}_bot_thick"))
            bot_color = lb2.text_input("Couleur hex", value=bot_line.get("color", "000000"), key=uk(f"{kp}_bot_color"))
            _cfg()[part]["_bottom_line"] = {"thickness_pt": bot_thick, "color": bot_color}
            st.markdown(f"<hr class='line-preview' style='border-color:#{bot_color}; border-top-width:{bot_thick}pt;'>",
                        unsafe_allow_html=True)
        else:
            _cfg()[part].pop("_bottom_line", None)

    # ── Colonne 3 : Distance du bord de page ──────────────────────────────
    with col_opts_r:
        st.markdown("**📏 Distance bord de page**")
        st.caption(
            "Espace entre le bord physique du papier et le début du "
            "header (ou footer). "
            "**Augmentez** cette valeur si votre contenu est trop près du bord "
            "ou rogné à l'impression. "
            "**Diminuez** si vous voulez maximiser la zone utile. "
            "Valeur 0 = Word utilise sa valeur par défaut (≈ 1.25 cm)."
        )
        cur_dist = cfg_part.get("_distance_cm", 1.25)
        new_dist = st.number_input(
            "Distance (cm)",
            value=float(cur_dist),
            min_value=0.0,
            max_value=5.0,
            step=0.25,
            key=uk(f"{kp}_dist"),
        )
        if new_dist > 0:
            _cfg()[part]["_distance_cm"] = round(new_dist, 2)
        else:
            _cfg()[part].pop("_distance_cm", None)
# ═════════════════════════════════════════════════════════════════════════
# CONSTRUCTION DU YAML PROPRE POUR PREVIEW / SAUVEGARDE
# ═════════════════════════════════════════════════════════════════════════

def _clean_element(elem: dict) -> dict:
    """
    Retourne un dict propre ne contenant QUE les champs pertinents
    pour le type déclaré dans elem["type"].
    Élimine les champs parasites laissés par des changements de type
    (ex: un élément text qui avait été image garde path/width_cm/height_cm).
    """
    etype = elem.get("type", "")
    # Champs communs à tous les types
    base = {"type": etype}

    if etype == "text":
        for k in ["value", "style", "align"]:
            if k in elem:
                base[k] = elem[k]

    elif etype == "image":
        for k in ["path", "width_cm", "height_cm", "align"]:
            if k in elem:
                base[k] = elem[k]

    elif etype == "floating_image":
        for k in ["path", "width_cm", "height_cm", "x_cm", "y_cm",
                  "wrap", "behind_text", "value"]:
            if k in elem:
                base[k] = elem[k]

    elif etype == "inline_group":
        for k in ["items", "align", "style", "value"]:
            if k in elem:
                base[k] = elem[k]

    elif etype == "horizontal_line":
        for k in ["thickness_pt", "color"]:
            if k in elem:
                base[k] = elem[k]

    elif etype == "field":
        for k in ["value"]:
            if k in elem:
                base[k] = elem[k]

    return base


def _render_live_preview():
    """
    Preview HTML live du header et footer actifs.
    Simule la mise en page 3 colonnes avec les valeurs textuelles actuelles.
    Affiche les noms des images (pas les images elles-mêmes — trop lourd).
    Les {{variables}} sont affichées telles quelles (non résolues à ce stade).
    """
    cfg = _cfg()

    def _elem_preview_html(elem: dict) -> str:
        """Rendu HTML simplifié d'un élément."""
        etype = elem.get("type", "")
        if etype == "text":
            val   = elem.get("value", "").replace("\n", "<br>")
            style = elem.get("style", {})
            color = f"#{style.get('color', '333333')}"
            size  = style.get("size", 9)
            bold  = "font-weight:700;" if style.get("bold") else ""
            return (f"<div style='font-size:{size}px; color:{color}; {bold} "
                    f"line-height:1.4; white-space:pre-wrap;'>{val}</div>")
        elif etype in ("image", "floating_image"):
            name = Path(elem.get("path", "image")).name
            w    = elem.get("width_cm", "?")
            return (f"<div style='background:#e3f2fd; border:1px solid #90caf9; "
                    f"border-radius:4px; padding:4px 8px; font-size:10px; color:#1565c0;'>"
                    f"🖼️ {name} ({w}cm)</div>")
        elif etype == "inline_group":
            items = elem.get("items", [])
            parts = []
            for it in items:
                v = it.get("value", "")
                parts.append(f"<span style='background:#e8f5e9; padding:1px 4px; "
                              f"border-radius:3px; font-size:10px;'>{v}</span>")
            return " ".join(parts)
        elif etype == "horizontal_line":
            color = f"#{elem.get('color', '000000')}"
            thick = elem.get("thickness_pt", 1)
            return f"<hr style='border:none; border-top:{thick}px solid {color}; margin:4px 0;'>"
        elif etype == "field":
            v = elem.get("value", "")
            return (f"<span style='background:#fff3e0; padding:2px 6px; "
                    f"border-radius:3px; font-size:10px; color:#e65100;'>[{v}]</span>")
        return ""

    def _zone_html(elems: list) -> str:
        return "".join(_elem_preview_html(e) for e in elems if e.get("type"))

    def _part_preview(part: str, label: str, bg: str, border: str) -> str:
        part_cfg = cfg.get(part, {})
        widths   = part_cfg.get("_col_widths", [1, 1, 1])
        total    = sum(widths) or 1
        pcts     = [int(w / total * 100) for w in widths]
        pcts[-1] = 100 - sum(pcts[:-1])

        left_h   = _zone_html(part_cfg.get("left",   []))
        center_h = _zone_html(part_cfg.get("center", []))
        right_h  = _zone_html(part_cfg.get("right",  []))

        has_content = any([left_h.strip(), center_h.strip(), right_h.strip()])
        if not has_content:
            return (f"<div style='background:{bg}; border:1px dashed {border}; "
                    f"border-radius:6px; padding:8px 12px; margin-bottom:8px; "
                    f"font-size:11px; color:#aaa; font-style:italic;'>"
                    f"{label} — vide</div>")

        return f"""
<div style='background:{bg}; border:1px solid {border}; border-radius:6px;
     padding:8px 12px; margin-bottom:8px;'>
  <div style='font-size:10px; font-weight:700; color:#555; margin-bottom:6px;
       text-transform:uppercase; letter-spacing:0.5px;'>{label}</div>
  <div style='display:flex; gap:4px;'>
    <div style='width:{pcts[0]}%; min-height:24px; padding:4px;
         border-right:1px dashed #ddd;'>{left_h}</div>
    <div style='width:{pcts[1]}%; min-height:24px; padding:4px;
         border-right:1px dashed #ddd; text-align:center;'>{center_h}</div>
    <div style='width:{pcts[2]}%; min-height:24px; padding:4px;
         text-align:right;'>{right_h}</div>
  </div>
</div>"""

    # Page simulée A4 (ratio)
    page_html = f"""
<div style='font-family:Calibri,sans-serif; max-width:720px; margin:0 auto;'>
  <div style='font-size:11px; color:#888; margin-bottom:6px;'>
    📄 Aperçu — les {{{{variables}}}} sont affichées non résolues
  </div>
  {_part_preview("header", "HEADER", "#f3f8ff", "#90caf9")}
  <div style='background:#fafafa; border:1px solid #eee; border-radius:6px;
       padding:16px; margin-bottom:8px; min-height:60px;
       font-size:11px; color:#bbb; font-style:italic; text-align:center;'>
    ··· Contenu du document ···
  </div>
  {_part_preview("footer", "FOOTER", "#f3fff3", "#a5d6a7")}
</div>"""

    with st.expander("👁️ Preview — aperçu visuel du header/footer", expanded=False):
        components.html(page_html, height=320, scrolling=False)


def _build_clean_config() -> dict:
    """
    Construit la config finale pour le YAML :
    - Retire les éléments vides (type == "")
    - Nettoie chaque élément des champs parasites (via _clean_element)
    - Conserve les clés spéciales (_col_widths, _top_line, _bottom_line, _distance_cm)
    - Retire les zones vides
    - Retire les parts entières vides
    """
    clean = {}
    for part in ["header", "footer", "header_first", "footer_first"]:
        part_data = _cfg().get(part, {})
        part_clean = {}

        # Clés spéciales (options avancées)
        for special in ["_col_widths", "_top_line", "_bottom_line", "_distance_cm"]:
            if special in part_data:
                part_clean[special] = part_data[special]

        # Zones — avec nettoyage de chaque élément
        for zone in ["left", "center", "right"]:
            elems = part_data.get(zone, [])
            if isinstance(elems, list):
                filtered = [
                    _clean_element(e)
                    for e in elems
                    if e.get("type", "")
                ]
                if filtered:
                    part_clean[zone] = filtered

        # N'inclure le part que s'il a du contenu
        has_zones   = any(k for k in part_clean if not k.startswith("_"))
        has_options = any(k for k in part_clean if k.startswith("_"))
        if has_zones or has_options:
            clean[part] = part_clean

    return clean


# ═════════════════════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═════════════════════════════════════════════════════════════════════════

# ── Appliquer la synchronisation options EN TÊTE DE PAGE (avant tout widget) ──
_apply_pending_sync()

st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
     padding: 28px 36px; border-radius: 14px; color: white; margin-bottom: 28px;'>
  <h1 style='margin:0; font-size:28px;'>🎨 Header &amp; Footer</h1>
  <p style='margin:6px 0 0; opacity:0.85;'>
    Créez et gérez vos presets de header/footer pour les documents Word
  </p>
</div>
""", unsafe_allow_html=True)

tab_builder, tab_presets, tab_images = st.tabs(
    ["✏️ Éditeur", "📂 Mes Presets", "🖼️ Images"]
)

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 : ÉDITEUR
# ══════════════════════════════════════════════════════════════════════════
with tab_builder:

    # ── Badge preset actif ────────────────────────────────────────────────
    active = st.session_state.get("active_preset_name")
    if active:
        st.markdown(
            f"<div style='background:#e8f5e9; border:2px solid #43a047; border-radius:10px; "
            f"padding:10px 18px; margin-bottom:16px; display:flex; align-items:center; gap:10px;'>"
            f"<span style='font-size:22px;'>✅</span>"
            f"<div><span style='font-size:13px; color:#2e7d32; font-weight:600;'>PRESET ACTIF</span>"
            f"<br><span style='font-size:18px; font-weight:800; color:#1b5e20;'>{active}</span></div>"
            f"</div>",
            unsafe_allow_html=True
        )
    else:
        st.info("💡 Aucun preset chargé — template par défaut ou config manuelle.")

    # ── 3 colonnes dans un expander ───────────────────────────────────────
    with st.expander("⚙️ Configuration — Templates, Variables & Options", expanded=False):
        col_left, col_mid, col_right = st.columns([3, 4, 2])

        # ── Colonne 1 : Template + Preset ─────────────────────────────────
        with col_left:
            st.markdown("**📋 Partir d'un template**")
            sel_tmpl = st.selectbox("", list(TEMPLATES.keys()), key="template_select",
                                    label_visibility="collapsed")
            if st.button("↩ Appliquer le template", key="apply_template", use_container_width=True):
                st.session_state.hf_config = copy.deepcopy(TEMPLATES[sel_tmpl])
                st.session_state.active_preset_name = None
                st.success(f"Template « {sel_tmpl} » appliqué !")
                _sync_section_options_to_state()
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**📂 Charger un preset existant**")
            preset_opts = get_preset_options("all")
            sel_preset  = st.selectbox("", list(preset_opts.keys()), key="load_preset_select",
                                       label_visibility="collapsed")
            if st.button("↩ Charger ce preset", key="load_preset_btn", use_container_width=True):
                ppath = preset_opts[sel_preset]
                if ppath == "none":
                    set_config({
                        "header": {"left": [], "center": [], "right": []},
                        "footer": {"left": [], "center": [], "right": []},
                    })
                    st.info("Config vide chargée")
                else:
                    loaded = load_preset(ppath)
                    if loaded:
                        for part in ["header", "footer"]:
                            loaded.setdefault(part, {})
                            for zone in ["left", "center", "right"]:
                                loaded[part].setdefault(zone, [])
                                loaded[part][zone] = [
                                    _clean_element(e)
                                    for e in loaded[part][zone]
                                    if e.get("type", "")
                                ]
                        set_config(loaded)
                        st.session_state.active_preset_name = Path(ppath).stem
                        _sync_section_options_to_state()
                        st.success(f"Preset « {Path(ppath).stem} » chargé !")
                        st.rerun()
                    else:
                        st.error("Impossible de charger ce preset")

        # ── Colonne 2 : Variables disponibles ─────────────────────────────
        with col_mid:
            st.markdown("**💡 Variables disponibles — cliquez pour copier**")
            st.caption("Clic → copie dans le presse-papier, puis Ctrl+V dans le champ Texte.")

            cat_colors = {
                "Consultant": "#7c4dff",
                "Document":   "#0277bd",
                "Agence":     "#2e7d32",
            }
            html_parts = []
            for cat, variables in VARIABLES_HELP.items():
                color = cat_colors.get(cat, "#555")
                html_parts.append(
                    f"<div style='margin-bottom:10px;'>"
                    f"<div style='font-size:11px; font-weight:700; color:{color}; "
                    f"text-transform:uppercase; letter-spacing:0.5px; margin-bottom:5px;'>"
                    f"{cat}</div>"
                    f"<div style='display:flex; flex-wrap:wrap; gap:5px;'>"
                )
                for var, desc in variables.items():
                    var_escaped = var.replace("'", "\\'")
                    html_parts.append(
                        f"<button onclick=\"copyVar('{var_escaped}', this)\" "
                        f"title=\"{desc}\" "
                        f"style='background:#f3f0ff; border:1.5px solid {color}; color:{color}; "
                        f"padding:3px 8px; border-radius:5px; font-size:11px; font-family:monospace; "
                        f"cursor:pointer; transition:all 0.15s;'>"
                        f"{var}</button>"
                    )
                html_parts.append("</div></div>")

            html_vars = "".join(html_parts)
            components.html(
                f"""
                <div id="var-panel">{html_vars}
                    <div id="toast" style="display:none; position:fixed; bottom:12px; right:12px;
                        background:#2e7d32; color:white; padding:6px 14px; border-radius:8px;
                        font-size:12px; font-family:sans-serif; z-index:9999;
                        box-shadow:0 2px 8px rgba(0,0,0,0.2);">✅ Copié !</div>
                </div>
                <script>
                function copyVar(v, btn) {{
                    navigator.clipboard.writeText(v).then(function() {{
                        var prev = btn.style.background;
                        btn.style.background = '#c8e6c9';
                        var t = document.getElementById('toast');
                        t.textContent = '✅ ' + v + ' copié !';
                        t.style.display = 'block';
                        setTimeout(function() {{ btn.style.background = prev; t.style.display = 'none'; }}, 1500);
                    }}).catch(function() {{
                        btn.style.background = '#ffccbc';
                        setTimeout(function() {{ btn.style.background = ''; }}, 1000);
                    }});
                }}
                </script>
                """,
                height=len(VARIABLES_HELP) * 68 + 10,
                scrolling=False,
            )

        # ── Colonne 3 : Première page différente ──────────────────────────
        with col_right:
            st.markdown("**📄 Options**")
            st.markdown("<br>", unsafe_allow_html=True)
            use_first_page = st.checkbox(
                "Première page différente",
                value=bool(_cfg().get("header_first") or _cfg().get("footer_first")),
                key="use_first_page",
                help="Si coché, configure un header/footer spécifiques pour la première page "
                     "(comportement Word titlePg)."
            )
            if use_first_page:
                _ensure_first_page_zones()
            else:
                _cfg().pop("header_first", None)
                _cfg().pop("footer_first", None)

    _ensure_zones()
    st.markdown(
        "<hr style='border:none; border-top:2px dashed #0000FF; margin:18px 0;'>",
        unsafe_allow_html=True
    )

    # ── Tabs Header / Footer ───────────────────────────────────────────────
    tab_hdr, tab_ftr = st.tabs(["🔝 Header", "🔻 Footer"])

    # ════════════════════════════════════════════════════════════════════════
    # TAB HEADER
    # ════════════════════════════════════════════════════════════════════════
    with tab_hdr:
        if use_first_page:
            sub_hdr_all, sub_hdr_first = st.tabs(["📄 Toutes les pages", "1️⃣ Première page seulement"])
        else:
            sub_hdr_all = st.container()

        with sub_hdr_all:
            st.markdown("""
            <div style='background:#fce4ec; padding:10px 16px; border-radius:8px;
                        border-left:5px solid #c62828; margin-bottom:14px;'>
                <strong style='color:#c62828;'>🔝 Header — Toutes les pages</strong>
            </div>""", unsafe_allow_html=True)
            _render_section_options("header")
            st.markdown("<br>", unsafe_allow_html=True)
            col_hl, col_hc, col_hr = st.columns(3)
            with col_hl: _render_zone_editor("header", "left")
            with col_hc: _render_zone_editor("header", "center")
            with col_hr: _render_zone_editor("header", "right")

        if use_first_page:
            with sub_hdr_first:
                st.markdown("""
                <div style='background:#fff3e0; padding:10px 16px; border-radius:8px;
                            border-left:5px solid #e65100; margin-bottom:14px;'>
                    <strong style='color:#e65100;'>1️⃣ Header — Première page uniquement</strong>
                </div>""", unsafe_allow_html=True)
                _render_section_options("header_first")
                st.markdown("<br>", unsafe_allow_html=True)
                col_hfl, col_hfc, col_hfr = st.columns(3)
                with col_hfl: _render_zone_editor("header_first", "left")
                with col_hfc: _render_zone_editor("header_first", "center")
                with col_hfr: _render_zone_editor("header_first", "right")

    # ════════════════════════════════════════════════════════════════════════
    # TAB FOOTER
    # ════════════════════════════════════════════════════════════════════════
    with tab_ftr:
        if use_first_page:
            sub_ftr_all, sub_ftr_first = st.tabs(["📄 Toutes les pages", "1️⃣ Première page seulement"])
        else:
            sub_ftr_all = st.container()

        with sub_ftr_all:
            st.markdown("""
            <div style='background:#e8f5e9; padding:10px 16px; border-radius:8px;
                        border-left:5px solid #2e7d32; margin-bottom:14px;'>
                <strong style='color:#2e7d32;'>🔻 Footer — Toutes les pages</strong>
            </div>""", unsafe_allow_html=True)
            _render_section_options("footer")
            st.markdown("<br>", unsafe_allow_html=True)
            col_fl, col_fc, col_fr = st.columns(3)
            with col_fl: _render_zone_editor("footer", "left")
            with col_fc: _render_zone_editor("footer", "center")
            with col_fr: _render_zone_editor("footer", "right")

        if use_first_page:
            with sub_ftr_first:
                st.markdown("""
                <div style='background:#e8eaf6; padding:10px 16px; border-radius:8px;
                            border-left:5px solid #3949ab; margin-bottom:14px;'>
                    <strong style='color:#3949ab;'>1️⃣ Footer — Première page uniquement</strong>
                </div>""", unsafe_allow_html=True)
                _render_section_options("footer_first")
                st.markdown("<br>", unsafe_allow_html=True)
                col_ffl, col_ffc, col_ffr = st.columns(3)
                with col_ffl: _render_zone_editor("footer_first", "left")
                with col_ffc: _render_zone_editor("footer_first", "center")
                with col_ffr: _render_zone_editor("footer_first", "right")

    # ── Preview HTML live ──────────────────────────────────────────────────
    st.markdown(
        "<hr style='border:none; border-top:2px dashed #0000FF; margin:18px 0;'>",
        unsafe_allow_html=True
    )
    _render_live_preview()

    # ── Aperçu YAML + Sauvegarde ───────────────────────────────────────────
    st.markdown(
        "<hr style='border:none; border-top:2px dashed #0000FF; margin:18px 0;'>",
        unsafe_allow_html=True
    )
    col_yaml, col_save = st.columns([3, 2])

    with col_yaml:
        st.markdown("### 👁️ Aperçu YAML")
        clean_cfg = _build_clean_config()
        yaml_str  = yaml.dump(clean_cfg, allow_unicode=True, default_flow_style=False, sort_keys=False)
        st.markdown(f'<div class="yaml-preview"><pre>{yaml_str}</pre></div>', unsafe_allow_html=True)
        st.download_button(
            "⬇️ Télécharger ce YAML",
            data=yaml_str.encode("utf-8"),
            file_name="custom_hf_preset.yaml",
            mime="text/yaml",
            use_container_width=True
        )

    with col_save:
        st.markdown("### 💾 Sauvegarder comme preset")
        preset_name = st.text_input("Nom du preset", value="mon_preset_custom", key="save_name")
        category    = st.selectbox("Catégorie", ["combined", "headers", "footers"], key="save_cat")
        overwrite   = st.checkbox("Écraser si existant", value=False, key="save_overwrite")
        if st.button("💾 Sauvegarder", type="primary", use_container_width=True):
            success, msg = save_preset(clean_cfg, preset_name, category, overwrite)
            if success:
                st.success(f"✅ {msg}")
                st.balloons()
            else:
                st.error(f"❌ {msg}")

        # Info sur les clés spéciales générées
        special_keys = [k for p in clean_cfg.values() if isinstance(p, dict) for k in p if k.startswith("_")]
        if special_keys:
            st.info(
                f"💡 Ce preset contient des options avancées : `{'`, `'.join(set(special_keys))}`\n\n"
                "Ces clés sont supportées par le moteur `docx_header_engine`."
            )


# ══════════════════════════════════════════════════════════════════════════
# TAB 2 : GESTION DES PRESETS
# ══════════════════════════════════════════════════════════════════════════
with tab_presets:
    st.markdown("### 📂 Presets disponibles")
    cat_filter = st.radio("Catégorie", ["Tous", "combined", "headers", "footers"], horizontal=True, key="preset_filter")
    cat_val    = "all" if cat_filter == "Tous" else cat_filter
    presets    = list_presets(cat_val)

    if not presets:
        st.info("Aucun preset trouvé. Créez-en un depuis l'onglet Éditeur !")
    else:
        active_name = st.session_state.get("active_preset_name")
        for p in presets:
            is_active = (p['name'] == active_name)
            # Conteneur coloré si actif
            row_style = (
                "background:#e8f5e9; border:2px solid #43a047; border-radius:8px; padding:6px 10px; margin-bottom:6px;"
                if is_active else
                "background:#fafafa; border:1px solid #e0e0e0; border-radius:8px; padding:6px 10px; margin-bottom:6px;"
            )
            st.markdown(f"<div style='{row_style}'>", unsafe_allow_html=True)
            c1, c2, c3, c4, c5 = st.columns([4, 2, 1, 1, 1])
            active_badge = " &nbsp;<span style='background:#43a047;color:white;padding:1px 7px;border-radius:8px;font-size:11px;font-weight:700;'>EN COURS</span>" if is_active else ""
            c1.markdown(
                f"**{p['icon']} {p['name']}**{active_badge}  \n"
                f"<small style='color:#888'>{p['modified']} — {p['size_kb']} KB</small>",
                unsafe_allow_html=True
            )
            tag_class = {"combined": "tag-combined", "headers": "tag-header", "footers": "tag-footer"}.get(p["category"], "tag-combined")
            c2.markdown(f"<span class='tag {tag_class}'>{p['category']}</span>", unsafe_allow_html=True)

            if c3.button("✏️", key=f"edit_{p['name']}_{p['category']}", help="Charger dans l'éditeur"):
                loaded = load_preset(p["path"])
                if loaded:
                    for part in ["header", "footer"]:
                        loaded.setdefault(part, {})
                        for zone in ["left", "center", "right"]:
                            loaded[part].setdefault(zone, [])
                            # Nettoyer les champs parasites à l'import
                            loaded[part][zone] = [
                                _clean_element(e)
                                for e in loaded[part][zone]
                                if e.get("type", "")
                            ]
                    set_config(loaded)
                    st.session_state.active_preset_name = p['name']
                    _sync_section_options_to_state()
                    st.success(f"« {p['name']} » chargé dans l'éditeur !")
                    st.rerun()

            if c4.button("📋", key=f"dup_{p['name']}_{p['category']}", help="Dupliquer"):
                ok, msg = duplicate_preset(p["path"], f"{p['name']}_copie")
                if ok: st.success(msg); st.rerun()
                else:  st.error(msg)

            if c5.button("🗑️", key=f"del_{p['name']}_{p['category']}", help="Supprimer"):
                ok, msg = delete_preset(p["path"])
                if ok:
                    if is_active:
                        st.session_state.active_preset_name = None
                    st.success(msg); st.rerun()
                else:  st.error(msg)

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⬆️ Importer un preset YAML")
    uploaded_yaml = st.file_uploader("Fichier .yaml", type=["yaml", "yml"], key="yaml_upload")
    if uploaded_yaml:
        ic, il = st.columns(2)
        import_cat  = ic.selectbox("Catégorie", ["combined", "headers", "footers"], key="import_cat")
        import_name = il.text_input("Nom", value=Path(uploaded_yaml.name).stem, key="import_name")
        if st.button("⬆️ Importer", key="do_import"):
            try:
                content = yaml.safe_load(uploaded_yaml.read())
                ok, msg = save_preset(content, import_name, import_cat, overwrite=True)
                if ok: st.success(f"✅ {msg}"); st.rerun()
                else:  st.error(msg)
            except Exception as e:
                st.error(f"Erreur de parsing YAML : {e}")


# ══════════════════════════════════════════════════════════════════════════
# TAB 3 : GESTION DES IMAGES
# ══════════════════════════════════════════════════════════════════════════
with tab_images:
    st.markdown("### 🖼️ Images disponibles pour les presets")

    with st.expander("⬆️ Uploader une nouvelle image", expanded=True):
        cu1, cu2 = st.columns([3, 1])
        with cu1:
            img_file = st.file_uploader("Image (JPG, PNG, GIF, WebP)", type=["jpg", "jpeg", "png", "gif", "webp", "bmp"], key="img_upload")
        with cu2:
            custom_name = st.text_input("Nom personnalisé (optionnel)", key="img_custom_name")
        if img_file and st.button("⬆️ Enregistrer l'image", key="do_img_upload"):
            filename = custom_name.strip() or None
            if filename and not Path(filename).suffix:
                filename = f"{filename}{Path(img_file.name).suffix}"
            ok, result = save_uploaded_image(img_file, filename)
            if ok: st.success(f"✅ Image sauvegardée : `{Path(result).name}`"); st.rerun()
            else:  st.error(f"❌ Erreur : {result}")

    st.markdown("---")
    images = list_available_images()
    if not images:
        st.info("Aucune image disponible.")
    else:
        builtin = [i for i in images if i["source"] == "builtin"]
        user    = [i for i in images if i["source"] == "user"]
        if builtin:
            st.markdown("**📦 Images intégrées**")
            cols = st.columns(4)
            for i, img in enumerate(builtin):
                with cols[i % 4]:
                    try: st.image(img["path"], caption=img["name"], use_container_width=True)
                    except: st.text(img["name"])
                    st.caption(f"`{Path(img['path']).name}`  ·  {img['size_kb']} KB")
        if user:
            st.markdown("**👤 Images uploadées**")
            cols = st.columns(4)
            for i, img in enumerate(user):
                with cols[i % 4]:
                    try: st.image(img["path"], caption=img["name"], use_container_width=True)
                    except: st.text(img["name"])
                    st.caption(f"`{Path(img['path']).name}`  ·  {img['size_kb']} KB")

    st.markdown("---")
    st.info(
        "💡 Dans l'onglet **Éditeur**, ajoutez un élément `Image` ou `Image flottante` "
        "et sélectionnez l'image dans la liste déroulante."
    )
