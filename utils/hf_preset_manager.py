"""
HF Preset Manager
Gère les presets de header/footer (chargement, sauvegarde, liste, upload images)

Dossier de presets :
  hf_presets/
    headers/   → presets header uniquement
    footers/   → presets footer uniquement
    combined/  → presets header+footer combinés (ex: akazi_standard.yaml)

Un preset est un fichier YAML compatible avec HeaderFooterEngine.apply_yaml().
"""

import yaml
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Racine du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dossiers de presets
HF_PRESETS_DIR  = PROJECT_ROOT / "hf_presets"
HEADERS_DIR     = HF_PRESETS_DIR / "headers"
FOOTERS_DIR     = HF_PRESETS_DIR / "footers"
COMBINED_DIR    = HF_PRESETS_DIR / "combined"

# Images uploadées par l'utilisateur
USER_IMAGES_DIR = PROJECT_ROOT / "Assets" / "user_uploads"

# Presets built-in (layouts/)
LAYOUTS_DIR     = PROJECT_ROOT / "layouts"

# ── Icônes type de preset ──────────────────────────────────────────────────
PRESET_ICONS = {
    "headers":  "🔝",
    "footers":  "🔻",
    "combined": "📄",
}


def ensure_dirs():
    """Crée les dossiers de presets s'ils n'existent pas"""
    for d in [HEADERS_DIR, FOOTERS_DIR, COMBINED_DIR, USER_IMAGES_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    _copy_builtin_presets()


def _copy_builtin_presets():
    """
    Copie les presets built-in depuis layouts/ vers hf_presets/combined/
    seulement s'ils n'y sont pas déjà.
    """
    if not LAYOUTS_DIR.exists():
        return

    for yaml_file in LAYOUTS_DIR.rglob("*.yaml"):
        dest = COMBINED_DIR / yaml_file.name
        if not dest.exists():
            shutil.copy2(yaml_file, dest)


# ── LISTE des presets ──────────────────────────────────────────────────────

def list_presets(category: str = "all") -> List[Dict]:
    """
    Liste les presets disponibles.

    Args:
        category: "headers" | "footers" | "combined" | "all"

    Returns:
        Liste de dicts avec : name, path, category, icon, modified
    """
    ensure_dirs()
    presets = []

    dirs = {
        "headers":  HEADERS_DIR,
        "footers":  FOOTERS_DIR,
        "combined": COMBINED_DIR,
    }

    if category == "all":
        search_dirs = dirs
    elif category in dirs:
        search_dirs = {category: dirs[category]}
    else:
        search_dirs = {}

    for cat, directory in search_dirs.items():
        for f in sorted(directory.glob("*.yaml")):
            presets.append({
                "name":     f.stem,
                "filename": f.name,
                "path":     str(f),
                "category": cat,
                "icon":     PRESET_ICONS.get(cat, "📄"),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "size_kb":  round(f.stat().st_size / 1024, 1),
            })

    return presets


def get_preset_options(category: str = "all") -> Dict[str, str]:
    """
    Retourne un dict {label_affichage: chemin_fichier} pour les selectbox Streamlit.
    Inclut toujours "— Aucun —" en premier.
    """
    options = {"— Aucun (pas de header/footer) —": "none"}

    presets = list_presets(category)
    for p in presets:
        label = f"{p['icon']} [{p['category']}] {p['name']}"
        options[label] = p["path"]

    return options


# ── CHARGEMENT / SAUVEGARDE ───────────────────────────────────────────────

def load_preset(preset_path: str) -> Optional[Dict]:
    """
    Charge un preset YAML.

    Returns:
        Dict de configuration ou None si erreur.
    """
    if not preset_path or preset_path == "none":
        return None

    path = Path(preset_path)
    if not path.exists():
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def save_preset(
    config: Dict,
    name: str,
    category: str = "combined",
    overwrite: bool = False
) -> Tuple[bool, str]:
    """
    Sauvegarde un preset YAML.

    Args:
        config:    Dict de configuration header/footer
        name:      Nom du preset (sans extension)
        category:  "headers" | "footers" | "combined"
        overwrite: Écrase si existant

    Returns:
        (success: bool, message: str)
    """
    ensure_dirs()

    dirs = {"headers": HEADERS_DIR, "footers": FOOTERS_DIR, "combined": COMBINED_DIR}
    directory = dirs.get(category, COMBINED_DIR)

    # Sanitize nom
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    dest = directory / f"{safe_name}.yaml"

    if dest.exists() and not overwrite:
        return False, f"Le preset '{safe_name}' existe déjà. Activez 'Écraser' pour remplacer."

    try:
        with open(dest, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return True, f"Preset '{safe_name}' sauvegardé dans {category}/"
    except Exception as e:
        return False, f"Erreur de sauvegarde : {e}"


def delete_preset(preset_path: str) -> Tuple[bool, str]:
    """Supprime un preset. Retourne (success, message)."""
    path = Path(preset_path)
    if not path.exists():
        return False, "Fichier introuvable"
    try:
        path.unlink()
        return True, f"Preset '{path.stem}' supprimé"
    except Exception as e:
        return False, str(e)


def duplicate_preset(preset_path: str, new_name: str) -> Tuple[bool, str]:
    """Duplique un preset existant sous un nouveau nom."""
    config = load_preset(preset_path)
    if config is None:
        return False, "Impossible de charger le preset source"

    # Déterminer la catégorie depuis le dossier parent
    parent = Path(preset_path).parent.name
    return save_preset(config, new_name, category=parent)


# ── GESTION DES IMAGES UTILISATEUR ───────────────────────────────────────

def save_uploaded_image(uploaded_file, filename: Optional[str] = None) -> Tuple[bool, str]:
    """
    Sauvegarde une image uploadée dans Assets/user_uploads/.

    Args:
        uploaded_file: Fichier Streamlit UploadedFile
        filename:      Nom personnalisé (optionnel, sinon nom original)

    Returns:
        (success: bool, path_or_error: str)
    """
    ensure_dirs()

    safe_name = filename or uploaded_file.name
    safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in safe_name)

    dest = USER_IMAGES_DIR / safe_name

    try:
        with open(dest, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return True, str(dest)
    except Exception as e:
        return False, str(e)


def list_available_images() -> List[Dict]:
    """
    Liste toutes les images disponibles (built-in + uploadées utilisateur).

    Returns:
        Liste de dicts avec : name, path, source ("builtin" | "user"), size_kb
    """
    ensure_dirs()
    images = []

    # Images built-in
    builtin_dir = PROJECT_ROOT / "Assets" / "images"
    if builtin_dir.exists():
        for f in sorted(builtin_dir.glob("*")):
            if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                images.append({
                    "name":    f.name,
                    "path":    str(f),
                    "source":  "builtin",
                    "label":   f"📦 {f.name} (intégré)",
                    "size_kb": round(f.stat().st_size / 1024, 1),
                })

    # Images utilisateur
    for f in sorted(USER_IMAGES_DIR.glob("*")):
        if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            images.append({
                "name":    f.name,
                "path":    str(f),
                "source":  "user",
                "label":   f"👤 {f.name} (uploadé)",
                "size_kb": round(f.stat().st_size / 1024, 1),
            })

    return images


def get_image_options() -> Dict[str, str]:
    """
    Retourne {label: path} pour les selectbox d'images dans le builder.
    """
    options = {"— Aucune image —": ""}
    for img in list_available_images():
        options[img["label"]] = img["path"]
    return options


# ── TEMPLATES DE DÉPART ───────────────────────────────────────────────────

TEMPLATE_EMPTY = {
    "header": {
        "left":   [],
        "center": [],
        "right":  [],
    },
    "footer": {
        "left":   [],
        "center": [],
        "right":  [],
    }
}

TEMPLATE_PAGE_NUMBER_ONLY = {
    "footer": {
        "right": [
            {
                "type":  "inline_group",
                "align": "right",
                "style": {"font": "Calibri", "size": 9, "color": "808080"},
                "items": [
                    {"type": "text",  "value": "Page "},
                    {"type": "field", "value": " PAGE "},
                    {"type": "text",  "value": " / "},
                    {"type": "field", "value": " NUMPAGES "},
                ]
            }
        ]
    }
}

TEMPLATE_AKAZI_STANDARD = {
    "header": {
        "left": [
            {"type": "image", "path": str(PROJECT_ROOT / "Assets" / "images" / "Akazi_logo_small.jpg"),
             "width_cm": 2.7, "height_cm": 1.4}
        ],
        "center": [
            {"type": "text", "value": "Vos consultants, de A à Z",
             "style": {"font": "Calibri", "size": 11, "bold": True, "color": "002060"}}
        ],
        "right": []
    },
    "footer": {
        "left": [
            {"type": "text", "value": "Société AKAZI, SAS – 60 Rue François 1er 75008 Paris",
             "style": {"font": "Calibri", "size": 8, "bold": True, "color": "002060"}}
        ],
        "center": [],
        "right": [
            {
                "type": "inline_group", "align": "right",
                "style": {"font": "Calibri", "size": 8, "bold": True, "color": "002060"},
                "items": [
                    {"type": "text",  "value": "Page "},
                    {"type": "field", "value": " PAGE "},
                    {"type": "text",  "value": " de "},
                    {"type": "field", "value": " NUMPAGES "},
                ]
            }
        ]
    }
}

TEMPLATES = {
    "Vide":                  TEMPLATE_EMPTY,
    "Numéro de page seul":   TEMPLATE_PAGE_NUMBER_ONLY,
    "AKAZI Standard":        TEMPLATE_AKAZI_STANDARD,
}
