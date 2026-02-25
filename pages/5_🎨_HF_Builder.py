"""
Page 5 — Éditeur Header/Footer (HF Builder) V4
NOUVEAUTÉS V4 :
  ✅ Highlight du preset actif dans "Mes Presets" + badge dans l'Éditeur
  ✅ Déplacer les éléments ↑ / ↓ dans chaque zone
  ✅ Liste de polices Word-safe avec option "Autre…"
"""

import streamlit as st
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

st.set_page_config(page_title="HF Builder", page_icon="🎨", layout="wide")

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
    .stTabs [data-baseweb="tab"] { font-weight: 600; }
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
def init_state():
    if 'hf_config' not in st.session_state:
        st.session_state.hf_config = copy.deepcopy(TEMPLATES["AKAZI Standard"])
    if '_pending_options_sync' not in st.session_state:
        st.session_state['_pending_options_sync'] = False
    if 'active_preset_name' not in st.session_state:
        st.session_state['active_preset_name'] = None  # Nom du preset chargé dans l'éditeur

init_state()

# ═════════════════════════════════════════════════════════════════════════
# SYNCHRONISATION session_state widgets ← hf_config (après chargement preset)
# ═════════════════════════════════════════════════════════════════════════

def _sync_section_options_to_state():
    """
    Demande une synchronisation des widgets options au prochain rendu.

    POURQUOI : Streamlit interdit de modifier session_state[key] APRÈS que
    le widget avec cette clé a été rendu dans le même cycle. Cette fonction
    positionne un FLAG qui sera lu en TÊTE DE PAGE (avant tout widget),
    au cycle suivant après st.rerun().
    """
    st.session_state["_pending_options_sync"] = True


def _apply_pending_sync():
    """
    Exécute la synchronisation si le flag est positionné.
    DOIT être appelé en tête de page, AVANT tout widget.
    """
    if not st.session_state.get("_pending_options_sync"):
        return
    st.session_state["_pending_options_sync"] = False

    for part in ["header", "footer"]:
        cfg = st.session_state.hf_config.get(part, {})
        kp  = f"opts_{part}"

        # _col_widths → widgets number_input Gauche/Centre/Droite
        col_widths = cfg.get("_col_widths", [1.0, 1.0, 1.0])
        while len(col_widths) < 3:
            col_widths.append(1.0)
        st.session_state[f"{kp}_cl"] = float(col_widths[0])
        st.session_state[f"{kp}_cc"] = float(col_widths[1])
        st.session_state[f"{kp}_cr"] = float(col_widths[2])

        # _top_line → checkbox + number_input + text_input
        top_line = cfg.get("_top_line", {})
        st.session_state[f"{kp}_top_on"]    = bool(top_line)
        st.session_state[f"{kp}_top_thick"] = float(top_line.get("thickness_pt", 1.0)) if top_line else 1.0
        st.session_state[f"{kp}_top_color"] = top_line.get("color", "000000") if top_line else "000000"

        # _bottom_line → idem
        bot_line = cfg.get("_bottom_line", {})
        st.session_state[f"{kp}_bot_on"]    = bool(bot_line)
        st.session_state[f"{kp}_bot_thick"] = float(bot_line.get("thickness_pt", 1.0)) if bot_line else 1.0
        st.session_state[f"{kp}_bot_color"] = bot_line.get("color", "000000") if bot_line else "000000"

        # _distance_cm → number_input
        dist = cfg.get("_distance_cm", 1.25)
        st.session_state[f"{kp}_dist"] = float(dist) if dist else 1.25


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
    """Selectbox police + champ libre si 'Autre…' choisi."""
    # Déterminer l'index dans FONT_LIST
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
        key=f"{kp}_type"
    )
    etype = next((t for t, l in ELEMENT_TYPE_LABELS.items() if l == sel_label), "")
    elem["type"] = etype

    if etype == "":
        st.caption("Élément vide — non inclus dans le YAML final.")
        return elem

    if etype == "text":
        elem["value"] = st.text_input("Texte", value=elem.get("value", ""), key=f"{kp}_val")
        style = elem.get("style", {})
        # Ligne 1 : Police (large) + Taille
        c1, c2 = st.columns([3, 1])
        with c1: style["font"] = _font_selector("Police", style.get("font", "Calibri"), f"{kp}_font")
        style["size"] = c2.number_input("Taille", value=int(style.get("size", 9)), min_value=6, max_value=36, key=f"{kp}_size")
        # Ligne 2 : Alignement + Gras + Couleur hex
        align_opts = ["left", "center", "right"]
        ca, cb, cc = st.columns([2, 1, 2])
        style["align"] = ca.selectbox("Alignement", align_opts, index=align_opts.index(style.get("align", "left")), key=f"{kp}_align")
        with cb:
            st.markdown("<br>", unsafe_allow_html=True)
            style["bold"] = st.checkbox("Gras", value=bool(style.get("bold", False)), key=f"{kp}_bold")
        style["color"] = cc.text_input("Couleur hex", value=style.get("color", "000000"), key=f"{kp}_color")
        elem["style"] = {k: v for k, v in style.items() if v not in [None, ""] or k == "bold"}

    elif etype == "image":
        img_opts = get_image_options()
        cur_path = elem.get("path", "")
        cur_il = next((l for l, p in img_opts.items() if p == cur_path), list(img_opts.keys())[0])
        elem["path"] = img_opts[st.selectbox("Image", list(img_opts.keys()), index=list(img_opts.keys()).index(cur_il), key=f"{kp}_imgpath")]
        c1, c2 = st.columns(2)
        elem["width_cm"] = c1.number_input("Largeur (cm)", value=float(elem.get("width_cm", 3.0)), min_value=0.5, max_value=20.0, step=0.1, key=f"{kp}_w")
        h = c2.number_input("Hauteur (cm) — 0 = auto", value=float(elem.get("height_cm", 0.0)), min_value=0.0, max_value=20.0, step=0.1, key=f"{kp}_h")
        if h > 0: elem["height_cm"] = h
        elif "height_cm" in elem: del elem["height_cm"]

    elif etype == "floating_image":
        img_opts = get_image_options()
        cur_path = elem.get("path", "")
        cur_il = next((l for l, p in img_opts.items() if p == cur_path), list(img_opts.keys())[0])
        elem["path"] = img_opts[st.selectbox("Image", list(img_opts.keys()), index=list(img_opts.keys()).index(cur_il), key=f"{kp}_fimgpath")]
        c1, c2, c3, c4 = st.columns(4)
        elem["width_cm"]  = c1.number_input("Largeur (cm)", value=float(elem.get("width_cm", 3.0)), min_value=0.5, max_value=20.0, step=0.1, key=f"{kp}_fw")
        elem["height_cm"] = c2.number_input("Hauteur (cm)", value=float(elem.get("height_cm", 1.5)), min_value=0.5, max_value=20.0, step=0.1, key=f"{kp}_fh")
        elem["x_cm"]      = c3.number_input("Position X (cm)", value=float(elem.get("x_cm", 0.0)), min_value=0.0, max_value=30.0, step=0.1, key=f"{kp}_fx")
        elem["y_cm"]      = c4.number_input("Position Y (cm)", value=float(elem.get("y_cm", 0.0)), min_value=0.0, max_value=30.0, step=0.1, key=f"{kp}_fy")
        wrap_opts = ["none", "tight", "square"]
        elem["wrap"] = st.selectbox("Wrapping", wrap_opts, index=wrap_opts.index(elem.get("wrap", "none")), key=f"{kp}_wrap")

    elif etype == "field":
        field_map = {" PAGE ": "Numéro de page", " NUMPAGES ": "Total pages", " DATE ": "Date", " TIME ": "Heure", " TITLE ": "Titre du document"}
        rev_map   = {v: k for k, v in field_map.items()}
        cur_fl    = field_map.get(elem.get("value", " PAGE "), "Numéro de page")
        elem["value"] = rev_map[st.selectbox("Champ Word", list(field_map.values()), index=list(field_map.values()).index(cur_fl), key=f"{kp}_field")]

    elif etype == "horizontal_line":
        c1, c2 = st.columns(2)
        elem["thickness_pt"] = c1.number_input("Épaisseur (pt)", value=int(elem.get("thickness_pt", 1)), min_value=1, max_value=10, key=f"{kp}_thick")
        elem["color"]        = c2.text_input("Couleur hex", value=elem.get("color", "000000"), key=f"{kp}_lcolor")

    elif etype == "inline_group":
        align_opts = ["left", "center", "right"]
        elem["align"] = st.selectbox("Alignement du groupe", align_opts, index=align_opts.index(elem.get("align", "right")), key=f"{kp}_galign")
        style = elem.get("style", {})
        c1, c2, c3 = st.columns(3)
        with c1: style["font"] = _font_selector("Police", style.get("font", "Calibri"), f"{kp}_gfont")
        style["size"]  = c2.number_input("Taille", value=int(style.get("size", 9)), min_value=6, max_value=36, key=f"{kp}_gsize")
        style["color"] = c3.text_input("Couleur hex", value=style.get("color", "808080"), key=f"{kp}_gcolor")
        elem["style"]  = style
        st.markdown("**Items du groupe** *(textes + champs sur une ligne)* :")
        items     = elem.get("items", [])
        new_items = []
        for i, item in enumerate(items):
            ci1, ci2, ci3 = st.columns([2, 4, 1])
            itype = ci1.selectbox("", ["text", "field"], index=0 if item.get("type") == "text" else 1, key=f"{kp}_it{i}_type", label_visibility="collapsed")
            ival  = ci2.text_input("", value=item.get("value", ""), key=f"{kp}_it{i}_val", label_visibility="collapsed")
            new_items.append({"type": itype, "value": ival})
            if ci3.button("✕", key=f"{kp}_it{i}_del", help="Supprimer"):
                new_items.pop()
                elem["items"] = new_items
                _update_element(part, zone, idx, elem)
                st.rerun()
        if st.button("➕ Ajouter un item", key=f"{kp}_additem"):
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
                if st.button("🗑️", key=f"del_{part}_{zone}_{i}",
                             help="Supprimer", use_container_width=True):
                    _delete_element(part, zone, i)
                    st.rerun()
            _update_element(part, zone, i, updated)
    if st.button(f"＋ Ajouter dans {zone_name}", key=f"add_{part}_{zone}", use_container_width=True):
        _add_element(part, zone)
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════
# OPTIONS AVANCÉES PAR SECTION (col_widths, marges, lignes full-width)
# ═════════════════════════════════════════════════════════════════════════

def _render_section_options(part: str):
    """
    Options avancées pour une section header ou footer.
    Version sans expander imbriqué (compatible Streamlit Cloud).
    """
    cfg_part = _cfg().get(part, {})
    kp = f"opts_{part}"

    # Toggle au lieu d'un expander imbriqué
    show_opts = st.toggle(
        f"⚙️ Options avancées ({part.upper()})",
        value=False,
        key=f"{kp}_toggle"
    )

    if not show_opts:
        return

    st.markdown("---")

    # ── Largeurs de colonnes ───────────────────────────────────────────
    st.markdown("**📐 Largeurs de colonnes** *(proportions relatives L / C / R)*")

    col_widths = cfg_part.get("_col_widths", [1, 1, 1])
    while len(col_widths) < 3:
        col_widths.append(1)

    c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
    w_left   = c1.number_input("Gauche",  value=float(col_widths[0]), min_value=0.1, max_value=10.0, step=0.5, key=f"{kp}_cl")
    w_center = c2.number_input("Centre",  value=float(col_widths[1]), min_value=0.1, max_value=10.0, step=0.5, key=f"{kp}_cc")
    w_right  = c3.number_input("Droite",  value=float(col_widths[2]), min_value=0.1, max_value=10.0, step=0.5, key=f"{kp}_cr")

    total = w_left + w_center + w_right
    with c4:
        pct_l = int(round(w_left   / total * 100))
        pct_c = int(round(w_center / total * 100))
        pct_r = 100 - pct_l - pct_c
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(f"→ {pct_l}% / {pct_c}% / {pct_r}%")

    _cfg()[part]["_col_widths"] = [
        round(w_left, 2),
        round(w_center, 2),
        round(w_right, 2)
    ]

    st.markdown("---")

    # ── Lignes horizontales full-width ──────────────────────────────────
    st.markdown("**─ Lignes horizontales** *(couvrent toute la largeur)*")

    col_top, col_bot = st.columns(2)

    # Ligne du dessus
    with col_top:
        st.markdown("**↑ Au-dessus du tableau**")
        top_line = cfg_part.get("_top_line", {})
        enable_top = st.checkbox("Activer", value=bool(top_line), key=f"{kp}_top_on")

        if enable_top:
            ct1, ct2 = st.columns(2)
            top_thick = ct1.number_input(
                "Épaisseur (pt)",
                value=float(top_line.get("thickness_pt", 1.0)),
                min_value=0.25,
                max_value=10.0,
                step=0.25,
                key=f"{kp}_top_thick"
            )
            top_color = ct2.text_input(
                "Couleur hex",
                value=top_line.get("color", "000000"),
                key=f"{kp}_top_color"
            )

            _cfg()[part]["_top_line"] = {
                "thickness_pt": top_thick,
                "color": top_color
            }

            st.markdown(
                f"<hr class='line-preview' style='border-color:#{top_color}; border-top-width:{top_thick}pt;'>",
                unsafe_allow_html=True
            )
        else:
            _cfg()[part].pop("_top_line", None)

    # Ligne du dessous
    with col_bot:
        st.markdown("**↓ En-dessous du tableau**")
        bot_line = cfg_part.get("_bottom_line", {})
        enable_bot = st.checkbox("Activer", value=bool(bot_line), key=f"{kp}_bot_on")

        if enable_bot:
            cb1, cb2 = st.columns(2)
            bot_thick = cb1.number_input(
                "Épaisseur (pt)",
                value=float(bot_line.get("thickness_pt", 1.0)),
                min_value=0.25,
                max_value=10.0,
                step=0.25,
                key=f"{kp}_bot_thick"
            )
            bot_color = cb2.text_input(
                "Couleur hex",
                value=bot_line.get("color", "000000"),
                key=f"{kp}_bot_color"
            )

            _cfg()[part]["_bottom_line"] = {
                "thickness_pt": bot_thick,
                "color": bot_color
            }

            st.markdown(
                f"<hr class='line-preview' style='border-color:#{bot_color}; border-top-width:{bot_thick}pt;'>",
                unsafe_allow_html=True
            )
        else:
            _cfg()[part].pop("_bottom_line", None)

    st.markdown("---")

    # ── Distance du bord de page ───────────────────────────────────────
    st.markdown("**📏 Distance du bord de page** *(en cm)*")

    cur_dist = cfg_part.get("_distance_cm", 1.25)

    new_dist = st.number_input(
        "Distance (cm)",
        value=float(cur_dist),
        min_value=0.0,
        max_value=5.0,
        step=0.25,
        key=f"{kp}_dist",
        help="Correspond à header_distance / footer_distance dans Word. 0 = valeur par défaut Word."
    )

    if new_dist > 0:
        _cfg()[part]["_distance_cm"] = round(new_dist, 2)
    else:
        _cfg()[part].pop("_distance_cm", None)
# ═════════════════════════════════════════════════════════════════════════
# CONSTRUCTION DU YAML PROPRE POUR PREVIEW / SAUVEGARDE
# ═════════════════════════════════════════════════════════════════════════

def _build_clean_config() -> dict:
    """
    Construit la config finale pour le YAML :
    - Retire les éléments vides (type == "")
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

        # Zones
        for zone in ["left", "center", "right"]:
            elems = part_data.get(zone, [])
            if isinstance(elems, list):
                filtered = [e for e in elems if e.get("type", "")]
                if filtered:
                    part_clean[zone] = filtered

        # N'inclure le part que s'il a du contenu
        if any(k for k in part_clean if not k.startswith("_")) or \
           any(k for k in part_clean if k.startswith("_")):
            # Inclure seulement si zones non vides OU options spéciales présentes
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
  <h1 style='margin:0; font-size:28px;'>🎨 Header/Footer Builder</h1>
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
    col_t, col_l, _ = st.columns([2, 2, 4])
    with col_t:
        sel_tmpl = st.selectbox("📋 Partir d'un template", list(TEMPLATES.keys()), key="template_select")
        if st.button("↩ Appliquer le template", key="apply_template"):
            st.session_state.hf_config = copy.deepcopy(TEMPLATES[sel_tmpl])
            st.session_state.active_preset_name = None
            st.success(f"Template « {sel_tmpl} » appliqué !")
            _sync_section_options_to_state()
            st.rerun()

    with col_l:
        preset_opts = get_preset_options("all")
        sel_preset  = st.selectbox("📂 Charger un preset existant", list(preset_opts.keys()), key="load_preset_select")
        if st.button("↩ Charger ce preset", key="load_preset_btn"):
            ppath = preset_opts[sel_preset]
            if ppath == "none":
                st.session_state.hf_config = {
                    "header": {"left": [], "center": [], "right": []},
                    "footer": {"left": [], "center": [], "right": []},
                }
                st.info("Config vide chargée")
            else:
                loaded = load_preset(ppath)
                if loaded:
                    for part in ["header", "footer"]:
                        loaded.setdefault(part, {})
                        for zone in ["left", "center", "right"]:
                            loaded[part].setdefault(zone, [])
                    st.session_state.hf_config = loaded
                    st.session_state.active_preset_name = Path(ppath).stem
                    _sync_section_options_to_state()
                    st.success(f"Preset « {Path(ppath).stem} » chargé !")
                    st.rerun()
                else:
                    st.error("Impossible de charger ce preset")

    st.markdown("---")
    _ensure_zones()

    # ── HEADER expander ───────────────────────────────────────────────────
    with st.expander("🔝  **HEADER**", expanded=True):
        # Options avancées en haut
        _render_section_options("header")
        st.markdown("<br>", unsafe_allow_html=True)
        # Colonnes de zones
        col_hl, col_hc, col_hr = st.columns(3)
        with col_hl: _render_zone_editor("header", "left")
        with col_hc: _render_zone_editor("header", "center")
        with col_hr: _render_zone_editor("header", "right")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── FOOTER expander ───────────────────────────────────────────────────
    with st.expander("🔻  **FOOTER**", expanded=True):
        _render_section_options("footer")
        st.markdown("<br>", unsafe_allow_html=True)
        col_fl, col_fc, col_fr = st.columns(3)
        with col_fl: _render_zone_editor("footer", "left")
        with col_fc: _render_zone_editor("footer", "center")
        with col_fr: _render_zone_editor("footer", "right")

    # ── Aperçu YAML + Sauvegarde ───────────────────────────────────────────
    st.markdown("---")
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
                    st.session_state.hf_config = loaded
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
