"""
AKAZI Générateur Batch V6.1
CORRECTIONS vs V6.0 :
  ✅ Fix faux doublons  : traitement fichiers conditionné au changement de hash
                          → les re-renders Streamlit ne re-traitent plus rien
  ✅ Tabs colorés V5    : 4 couleurs distinctes (violet / vert / rose / bleu ciel)
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
import yaml
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import io
import zipfile
import sys
import tempfile
import traceback

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from generators.akazi_cv_generator import AkaziCVGenerator
    from generators.mc2i_cv_generator import MC2ICVGenerator
    from generators.akazi_jobdesc_generator import AkaziJobDescGenerator
    GENERATORS_AVAILABLE = True
except ImportError as e:
    GENERATORS_AVAILABLE = False
    print(f"Warning: {e}")

try:
    from utils.hf_preset_manager import get_preset_options, ensure_dirs
    ensure_dirs()
    HF_MANAGER_AVAILABLE = True
except ImportError:
    HF_MANAGER_AVAILABLE = False

st.set_page_config(
    page_title="AKAZI Generator",
    page_icon="📄",
    layout="wide"
)

# ── CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px; border-radius: 15px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 30px rgba(102,126,234,0.3);
        text-align: center;
    }
    .main-header h1 { margin: 0; font-size: 36px; font-weight: 700; }

    .upload-section {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin-bottom: 30px;
        border-left: 5px solid #667eea;
    }

    /* ─── Tabs colorés (restauration V5) ────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; padding: 0; }

    .stTabs [data-baseweb="tab"] {
        height: 60px; border-radius: 10px 10px 0 0;
        padding: 15px 25px; font-weight: 600; font-size: 15px;
        border: 2px solid #e0e0e0; border-bottom: none;
        transition: all 0.3s;
    }

    /* Tab 1 — Violet (Fichiers & Génération) */
    .stTabs [data-baseweb="tab"]:nth-child(1) {
        background: linear-gradient(135deg, #667eea50 0%, #764ba250 100%);
        color: #667eea;
    }
    .stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102,126,234,0.4);
    }

    /* Tab 2 — Vert (Documents Générés) */
    .stTabs [data-baseweb="tab"]:nth-child(2) {
        background: linear-gradient(135deg, #11998e50 0%, #38ef7d50 100%);
        color: #11998e;
    }
    .stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white; transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(17,153,142,0.4);
    }

    /* Tab 3 — Rose (Logs) */
    .stTabs [data-baseweb="tab"]:nth-child(3) {
        background: linear-gradient(135deg, #f093fb50 0%, #f5576c50 100%);
        color: #d63a6a;
    }
    .stTabs [data-baseweb="tab"]:nth-child(3)[aria-selected="true"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white; transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(240,147,251,0.4);
    }

    /* Tab 4 — Bleu ciel (Statistiques) */
    .stTabs [data-baseweb="tab"]:nth-child(4) {
        background: linear-gradient(135deg, #4facfe50 0%, #00f2fe50 100%);
        color: #1a8ccc;
    }
    .stTabs [data-baseweb="tab"]:nth-child(4)[aria-selected="true"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white; transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79,172,254,0.4);
    }

    /* ─── Badges ─────────────────────────────────────────────────────── */
    .badge-success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white; padding: 4px 10px; border-radius: 12px;
        font-size: 11px; font-weight: 600;
    }
    .badge-error {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white; padding: 4px 10px; border-radius: 12px;
        font-size: 11px; font-weight: 600;
    }

    /* ─── Bouton principal ───────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 12px 30px;
        font-size: 16px; font-weight: 600; border-radius: 10px;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }

    /* ─── Encart sélecteur H/F par fichier ──────────────────────────── */
    .hf-selector {
        background: #f0f4ff; border-radius: 10px;
        padding: 12px 16px; border-left: 4px solid #667eea;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ── CONFIG ────────────────────────────────────────────────────────────────
ALL_POSSIBLE_FORMATS = ['JD-AKAZI-FR', 'JD-AKAZI-EN', 'CV-AKAZI', 'CV-MC2I']


def get_available_formats(document_type, format_code, language_iso=None):
    if not document_type or not format_code:
        return []
    if document_type == "job_description":
        if "AKAZI" in format_code:
            lang = (language_iso or '').upper()
            if lang == 'FRA':   return ["JD-AKAZI-FR"]
            elif lang == 'ENG': return ["JD-AKAZI-EN"]
            else:               return ["JD-AKAZI-FR", "JD-AKAZI-EN"]
        return []
    elif document_type == "cv":
        if format_code == "AKAZI_V1": return ["CV-AKAZI"]
        elif format_code == "MC2I_V1": return ["CV-MC2I"]
        return []
    return []


# ── SESSION STATE ─────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        'files_data':          [],
        'duplicate_files':     [],
        'generated_documents': {},
        'processing_logs':     [],
        'statistics': {
            'total_uploaded': 0, 'total_generated': 0,
            'total_errors': 0,   'generation_times': []
        },
        'selections':      {},
        'hf_selections':   {},
        'uploader_key':    0,
        'last_files_hash': None,   # ← clé centrale du fix doublon
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_all():
    for key in ['files_data', 'duplicate_files', 'generated_documents',
                'processing_logs', 'statistics', 'selections',
                'hf_selections', 'last_files_hash']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.uploader_key += 1
    init_session_state()


init_session_state()


# ── HELPERS ───────────────────────────────────────────────────────────────

def add_log(level: str, message: str):
    st.session_state.processing_logs.append({
        'level':     level,
        'message':   message,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })


def load_file_data(uploaded_file) -> Optional[Dict]:
    try:
        content = uploaded_file.read()
        uploaded_file.seek(0)
        if uploaded_file.name.endswith('.json'):
            return json.loads(content)
        elif uploaded_file.name.endswith(('.yaml', '.yml')):
            return yaml.safe_load(content)
    except Exception as e:
        add_log('error', f"Erreur lecture {uploaded_file.name}: {e}")
    return None


def extract_metadata(data: Dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    try:
        if 'document_metadata' in data:
            meta = data['document_metadata']
            return (meta.get('document_type'),
                    meta.get('format_code'),
                    meta.get('language_iso'))
        # Fallback heuristique
        if all(k in data for k in ['header', 'sections', 'metadata']):
            if 'job_id' in data.get('metadata', {}):
                return ('job_description', 'AKAZI_JD', None)
        if all(k in data for k in ['str_Initials', 'experiences']):
            fmt = data.get('document_metadata', {}).get('format_code', 'AKAZI_V1')
            return ('cv', fmt, None)
        if all(k in data for k in ['document_metadata', 'introduction',
                                    'professional_experiences']):
            return ('cv', 'MC2I_V1', None)
    except Exception:
        pass
    return (None, None, None)


def _build_combined_hf_preset(header_path: str, footer_path: str) -> Optional[str]:
    """Combine preset header + footer en un fichier YAML temporaire."""
    if header_path == "none" and footer_path == "none":
        return None
    combined = {}
    if header_path and header_path != "none":
        try:
            with open(header_path, 'r', encoding='utf-8') as f:
                hcfg = yaml.safe_load(f)
            for k in ['header', 'header_first', 'header_even']:
                if k in hcfg:
                    combined[k] = hcfg[k]
        except Exception:
            pass
    if footer_path and footer_path != "none":
        try:
            with open(footer_path, 'r', encoding='utf-8') as f:
                fcfg = yaml.safe_load(f)
            for k in ['footer', 'footer_first', 'footer_even']:
                if k in fcfg:
                    combined[k] = fcfg[k]
        except Exception:
            pass
    if not combined:
        return "none"
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                      delete=False, encoding='utf-8')
    yaml.safe_dump(combined, tmp, allow_unicode=True, default_flow_style=False)
    tmp.close()
    return tmp.name


def generate_document(data: Dict, fmt: str, filename: str,
                       hf_preset: Optional[str] = None) -> Optional[bytes]:
    """Génère un document Word et retourne ses bytes."""
    generate_document._last_hf_error = None  # reset avant chaque génération
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                          delete=False, encoding='utf-8') as tf:
            json.dump(data, tf, ensure_ascii=False)
            input_path = Path(tf.name)

        output_path = input_path.parent / f"output_{fmt}.docx"
        kwargs = {}
        if hf_preset is not None:
            kwargs['hf_preset'] = hf_preset

        if fmt in ('JD-AKAZI-FR', 'JD-AKAZI-EN'):
            lang = 'fr' if fmt == 'JD-AKAZI-FR' else 'en'
            gen = AkaziJobDescGenerator(input_path, output_path, lang=lang, **kwargs)
        elif fmt == 'CV-AKAZI':
            gen = AkaziCVGenerator(input_path, output_path, **kwargs)
        elif fmt == 'CV-MC2I':
            gen = MC2ICVGenerator(input_path, output_path, **kwargs)
        else:
            add_log('error', f"Format inconnu: {fmt}")
            return None

        gen.generate()
        # Récupérer l'erreur HF éventuelle
        if hasattr(gen, '_hf_error') and gen._hf_error:
            generate_document._last_hf_error = gen._hf_error

        with open(output_path, 'rb') as f:
            doc_bytes = f.read()

        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
        add_log('success', f"✅ {filename} → {fmt} généré")
        return doc_bytes

    except Exception as e:
        add_log('error', f"❌ {filename} → {fmt} : {e}")
        traceback.print_exc()
        return None


# ═════════════════════════════════════════════════════════════════════════
# INTERFACE
# ═════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="main-header">
  <h1>📄 AKAZI Document Generator</h1>
  <p style='margin:8px 0 0; opacity:0.85; font-size:16px;'>
    Transformez vos fichiers JSON/YAML en documents Word professionnels
  </p>
</div>
""", unsafe_allow_html=True)

# ── Header/Footer global ──────────────────────────────────────────────────
if HF_MANAGER_AVAILABLE:
    with st.expander(
        "⚙️ Header/Footer global (appliqué à tous les fichiers sans preset spécifique)",
        expanded=False
    ):
        preset_opts = get_preset_options("all")
        col_gh, col_gf = st.columns(2)
        with col_gh:
            global_header = st.selectbox(
                "🔝 Header global", list(preset_opts.keys()),
                key="global_header_preset"
            )
        with col_gf:
            global_footer = st.selectbox(
                "🔻 Footer global", list(preset_opts.keys()),
                key="global_footer_preset"
            )
        st.caption("💡 Vous pouvez surcharger ces choix fichier par fichier ci-dessous.")
else:
    preset_opts   = {}
    global_header = "none"
    global_footer = "none"

# ── Upload ────────────────────────────────────────────────────────────────
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
col_up1, col_up2 = st.columns([3, 1])
with col_up1:
    uploaded_files = st.file_uploader(
        "📁 Uploadez vos fichiers JSON/YAML",
        type=['json', 'yaml', 'yml'],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}"
    )
with col_up2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Réinitialiser tout", use_container_width=True):
        reset_all()
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── Traitement fichiers — FIX DOUBLON ─────────────────────────────────────
# Tout le traitement est dans le bloc "if hash_changed".
# Un re-render Streamlit sans changement de fichiers tombe dans le else
# implicite et ne fait rien → plus de faux doublons.
if uploaded_files:
    current_files_hash = hashlib.md5(
        ''.join([f.name + str(f.size) for f in uploaded_files]).encode()
    ).hexdigest()

    if st.session_state.last_files_hash != current_files_hash:
        # Nouveau batch : réinitialiser proprement avant tout traitement
        st.session_state.files_data      = []
        st.session_state.duplicate_files = []
        st.session_state.hf_selections   = {}
        st.session_state.last_files_hash = current_files_hash

        seen_stems               = {}
        existing_content_hashes  = set()   # vide → nouveau batch garanti

        for idx, uf in enumerate(uploaded_files, 1):
            try:
                data = load_file_data(uf)
                if not data:
                    st.warning(f"⚠️ Impossible de lire {uf.name}")
                    continue

                # ── Doublon par contenu (hash MD5 du JSON normalisé) ─────
                content_hash = hashlib.md5(
                    json.dumps(data, sort_keys=True).encode()
                ).hexdigest()

                if content_hash in existing_content_hashes:
                    st.session_state.duplicate_files.append(uf.name)
                    add_log('warning', f"Doublon ignoré : {uf.name}")
                    continue

                existing_content_hashes.add(content_hash)

                # ── Métadonnées ──────────────────────────────────────────
                doc_type, fmt_code, lang_iso = extract_metadata(data)
                available = get_available_formats(doc_type, fmt_code, lang_iso)

                if not doc_type or not fmt_code:
                    add_log('warning',
                            f"{uf.name} : métadonnées manquantes (document_metadata)")

                # ── Stem unique (doublons de nom de fichier) ─────────────
                raw_stem = Path(uf.name).stem
                if raw_stem in seen_stems:
                    seen_stems[raw_stem] += 1
                    internal_stem = f"{raw_stem}_{seen_stems[raw_stem]}"
                else:
                    seen_stems[raw_stem] = 0
                    internal_stem = raw_stem

                file_hash = hashlib.md5(
                    f"{idx}_{internal_stem}".encode()
                ).hexdigest()[:8]

                st.session_state.files_data.append({
                    'id':                idx,
                    'filename':          uf.name,
                    'stem':              raw_stem,
                    'file_hash':         file_hash,
                    'content_hash':      content_hash,
                    'doc_type':          doc_type,
                    'format_code':       fmt_code,
                    'language_iso':      lang_iso,
                    'available_outputs': available,
                    'data':              data,
                })

                for fmt in available:
                    key = f"{idx}_{fmt}_{file_hash}"
                    st.session_state.selections[key] = True

                st.session_state.statistics['total_uploaded'] += 1

            except Exception as e:
                add_log('error', f"Erreur {uf.name}: {e}")
                traceback.print_exc()

        add_log('info',
                f"{len(st.session_state.files_data)} fichier(s) chargé(s), "
                f"{len(st.session_state.duplicate_files)} doublon(s) ignoré(s)")

    # ── TABS — affichés à chaque render (hash changé ou non) ─────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Fichiers & Génération",
        "📥 Documents Générés",
        "📊 Logs",
        "📈 Statistiques"
    ])

    if st.session_state.files_data:

        # ══════════════════════════════════════════════════════════════════
        # TAB 1 — Fichiers & Génération
        # ══════════════════════════════════════════════════════════════════
        with tab1:
            n = len(st.session_state.files_data)
            st.markdown(f"### {n} fichier(s) chargé(s)")

            # Options HF (avec option "Par défaut global" en tête)
            if HF_MANAGER_AVAILABLE:
                hf_opts_raw = get_preset_options("all")
            else:
                hf_opts_raw = {}

            hf_opts_full = {"— Par défaut global —": "__global__"}
            hf_opts_full.update(hf_opts_raw)

            # Boutons sélection globale
            col_sa, col_da, _ = st.columns([1, 1, 4])
            with col_sa:
                if st.button("☑️ Tout sélectionner", use_container_width=True):
                    for fi in st.session_state.files_data:
                        for fmt in fi['available_outputs']:
                            st.session_state.selections[
                                f"{fi['id']}_{fmt}_{fi['file_hash']}"
                            ] = True
                    st.rerun()
            with col_da:
                if st.button("☐ Tout déselectionner", use_container_width=True):
                    st.session_state.selections = {}
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Carte par fichier avec ranking ──────────────────────────────────
            n_files = len(st.session_state.files_data)
            for rank, file_info in enumerate(st.session_state.files_data):
                fid = file_info['id']

                # ── Ligne de ranking : numéro + boutons ↑↓ ──────────────────
                col_rank, col_up, col_dn, col_title = st.columns([1, 1, 1, 20])
                with col_rank:
                    st.markdown(
                        f"<div style='background:linear-gradient(135deg,#667eea,#764ba2);"
                        f"color:white;border-radius:50%;width:32px;height:32px;"
                        f"display:flex;align-items:center;justify-content:center;"
                        f"font-weight:700;font-size:14px;margin-top:4px;'>"
                        f"{rank + 1}</div>",
                        unsafe_allow_html=True
                    )
                with col_up:
                    # Monter — désactivé pour le premier
                    if rank > 0:
                        if st.button("▲", key=f"rank_up_{fid}_{rank}", help="Monter"):
                            fd = st.session_state.files_data
                            fd[rank - 1], fd[rank] = fd[rank], fd[rank - 1]
                            st.rerun()
                    else:
                        st.write("")
                with col_dn:
                    # Descendre — désactivé pour le dernier
                    if rank < n_files - 1:
                        if st.button("▼", key=f"rank_dn_{fid}_{rank}", help="Descendre"):
                            fd = st.session_state.files_data
                            fd[rank], fd[rank + 1] = fd[rank + 1], fd[rank]
                            st.rerun()
                    else:
                        st.write("")

                with st.expander(
                    f"📄 {file_info['filename']}  ·  "
                    f"`{file_info.get('format_code','?')}`",
                    expanded=True
                ):
                    col_meta, col_fmt, col_hf = st.columns([2, 2, 3])

                    with col_meta:
                        st.markdown(f"**Type :** `{file_info.get('doc_type','?')}`")
                        st.markdown(f"**Format :** `{file_info.get('format_code','?')}`")
                        st.markdown(
                            f"**Langue :** `{file_info.get('language_iso') or '—'}`"
                        )

                    with col_fmt:
                        st.markdown("**Formats de sortie :**")
                        avail = file_info['available_outputs']
                        if avail:
                            for fmt in avail:
                                key = f"{fid}_{fmt}_{file_info['file_hash']}"
                                st.session_state.selections[key] = st.checkbox(
                                    fmt,
                                    value=st.session_state.selections.get(key, True),
                                    key=f"chk_{key}"
                                )
                        else:
                            st.warning("⚠️ Format non reconnu")

                    with col_hf:
                        if HF_MANAGER_AVAILABLE:
                            st.markdown(
                                '<div class="hf-selector">',
                                unsafe_allow_html=True
                            )
                            st.markdown("**🎨 Header/Footer spécifique :**")

                            if fid not in st.session_state.hf_selections:
                                st.session_state.hf_selections[fid] = {
                                    'header': "— Par défaut global —",
                                    'footer': "— Par défaut global —"
                                }

                            c_h, c_f = st.columns(2)
                            with c_h:
                                cur_h = st.session_state.hf_selections[fid].get(
                                    'header', "— Par défaut global —"
                                )
                                sel_h = st.selectbox(
                                    "🔝 Header",
                                    list(hf_opts_full.keys()),
                                    index=list(hf_opts_full.keys()).index(cur_h)
                                          if cur_h in hf_opts_full else 0,
                                    key=f"hf_h_{fid}"
                                )
                                st.session_state.hf_selections[fid]['header'] = sel_h

                            with c_f:
                                cur_f = st.session_state.hf_selections[fid].get(
                                    'footer', "— Par défaut global —"
                                )
                                sel_f = st.selectbox(
                                    "🔻 Footer",
                                    list(hf_opts_full.keys()),
                                    index=list(hf_opts_full.keys()).index(cur_f)
                                          if cur_f in hf_opts_full else 0,
                                    key=f"hf_f_{fid}"
                                )
                                st.session_state.hf_selections[fid]['footer'] = sel_f

                            st.markdown('</div>', unsafe_allow_html=True)

            # Doublons dans un expander séparé — sans action possible
            if st.session_state.duplicate_files:
                n_dup = len(st.session_state.duplicate_files)
                with st.expander(
                    f"🔴 {n_dup} fichier(s) ignoré(s) — contenu identique à un fichier déjà chargé",
                    expanded=False
                ):
                    st.caption(
                        "Ces fichiers ont été ignorés automatiquement car leur contenu "
                        "est identique à un fichier déjà présent dans la session. "
                        "Ils ne seront pas générés."
                    )
                    for name in st.session_state.duplicate_files:
                        st.markdown(
                            f"<div style='padding:6px 12px; margin:3px 0; "
                            f"background:#fff0f0; border-left:3px solid #cc0000; "
                            f"border-radius:4px; font-size:13px;'>"
                            f"📄 {name}"
                            f"</div>",
                            unsafe_allow_html=True
                        )

            # Bouton Générer
            st.markdown("<br>", unsafe_allow_html=True)
            total_sel = sum(1 for v in st.session_state.selections.values() if v)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    f"🚀 Générer ({total_sel} sélectionné(s))",
                    disabled=(total_sel == 0 or not GENERATORS_AVAILABLE),
                    use_container_width=True
                ):
                    progress_bar = st.progress(0)
                    status_text  = st.empty()
                    generated_count = 0
                    error_count     = 0
                    tasks = [
                        (fi, fmt)
                        for fi in st.session_state.files_data
                        for fmt in fi['available_outputs']
                        if st.session_state.selections.get(
                            f"{fi['id']}_{fmt}_{fi['file_hash']}"
                        )
                    ]

                    generation_ts      = datetime.now().strftime("%Y-%m-%d %H%M%S")
                    output_name_counts = {}

                    for idx, (file_info, fmt) in enumerate(tasks):
                        fid = file_info['id']
                        status_text.text(
                            f"Génération {idx+1}/{len(tasks)}: "
                            f"{file_info['filename']} → {fmt}"
                        )
                        progress_bar.progress((idx + 1) / len(tasks))

                        # Résoudre preset HF
                        hf_preset_path = None
                        if HF_MANAGER_AVAILABLE:
                            hf_sel  = st.session_state.hf_selections.get(fid, {})
                            h_label = hf_sel.get('header', "— Par défaut global —")
                            f_label = hf_sel.get('footer', "— Par défaut global —")

                            h_path = hf_opts_full.get(h_label, "__global__")
                            f_path = hf_opts_full.get(f_label, "__global__")

                            global_h = preset_opts.get(global_header, "none")
                            global_f = preset_opts.get(global_footer, "none")
                            if h_path == "__global__": h_path = global_h
                            if f_path == "__global__": f_path = global_f

                            if h_path or f_path:
                                hf_preset_path = _build_combined_hf_preset(
                                    h_path, f_path
                                )

                        start_time = datetime.now()
                        doc_bytes  = generate_document(
                            file_info['data'], fmt,
                            file_info['filename'],
                            hf_preset=hf_preset_path
                        )
                        elapsed = (datetime.now() - start_time).total_seconds()
                        # Afficher erreur HF si présente
                        if getattr(generate_document, '_last_hf_error', None):
                            st.warning(
                                f"⚠️ **Header/Footer non appliqué** pour `{file_info['filename']}`\n\n"
                                f"```\n{generate_document._last_hf_error[:800]}\n```"
                            )
                        # Afficher les erreurs HF si le moteur a eu un problème
                        if hasattr(generate_document, '_last_hf_error') and generate_document._last_hf_error:
                            st.warning(f"⚠️ HF preset non appliqué pour {file_info['filename']}: {generate_document._last_hf_error}")
                            generate_document._last_hf_error = None

                        # Cleanup YAML temporaire
                        if hf_preset_path and hf_preset_path not in ("none", None):
                            try:
                                Path(hf_preset_path).unlink(missing_ok=True)
                            except Exception:
                                pass

                        if doc_bytes:
                            base_name = (
                                f"{file_info['stem']}_{fmt}__V{generation_ts}"
                            )
                            if base_name in output_name_counts:
                                output_name_counts[base_name] += 1
                                output_filename = (
                                    f"{base_name} "
                                    f"({output_name_counts[base_name]}).docx"
                                )
                            else:
                                output_name_counts[base_name] = 0
                                output_filename = f"{base_name}.docx"

                            dl_key = (
                                f"dl_{fid}_{fmt}_{file_info['file_hash']}_{idx}"
                            )
                            st.session_state.generated_documents[dl_key] = {
                                'filename':  output_filename,
                                'format':    fmt,
                                'data':      doc_bytes,
                                'mime_type': (
                                    'application/vnd.openxmlformats-officedocument'
                                    '.wordprocessingml.document'
                                ),
                                'dl_key':    dl_key,
                            }
                            st.session_state.statistics[
                                'generation_times'
                            ].append(elapsed)
                            generated_count += 1
                        else:
                            error_count += 1

                    st.session_state.statistics['total_generated'] += generated_count
                    st.session_state.statistics['total_errors']    += error_count
                    progress_bar.empty()
                    status_text.empty()

                    if generated_count > 0:
                        st.success(f"✅ {generated_count} document(s) généré(s) !")
                    if error_count > 0:
                        st.error(
                            f"❌ {error_count} erreur(s) — voir l'onglet Logs"
                        )
                    st.rerun()

        # ══════════════════════════════════════════════════════════════════
        # TAB 2 — Documents Générés
        # ══════════════════════════════════════════════════════════════════
        with tab2:
            st.markdown("### 📥 Documents Générés")
            if st.session_state.generated_documents:
                for doc in st.session_state.generated_documents.values():
                    c1, c2, c3 = st.columns([4, 2, 1])
                    c1.markdown(f"**{doc['filename']}**")
                    c2.markdown(
                        f"<span class='badge-success'>{doc['format']}</span>",
                        unsafe_allow_html=True
                    )
                    c3.download_button(
                        "⬇️", data=doc['data'],
                        file_name=doc['filename'],
                        mime=doc['mime_type'],
                        key=doc['dl_key']
                    )

                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button(
                        "📦 Télécharger tout en ZIP",
                        use_container_width=True
                    ):
                        zip_buf = io.BytesIO()
                        with zipfile.ZipFile(
                            zip_buf, 'w', zipfile.ZIP_DEFLATED
                        ) as zf:
                            for doc in st.session_state.generated_documents.values():
                                zf.writestr(doc['filename'], doc['data'])
                        zip_buf.seek(0)
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            "⬇️ Télécharger le ZIP",
                            data=zip_buf.getvalue(),
                            file_name=f"Documents_AKAZI_{ts}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
            else:
                st.info("📭 Aucun document généré pour l'instant")

        # ══════════════════════════════════════════════════════════════════
        # TAB 3 — Logs
        # ══════════════════════════════════════════════════════════════════
        with tab3:
            st.markdown("### 📊 Logs de traitement")
            if st.session_state.processing_logs:
                for log in reversed(st.session_state.processing_logs[-30:]):
                    badge = (
                        'badge-success'
                        if log['level'] in ['info', 'success']
                        else 'badge-error'
                    )
                    st.markdown(f"""
                    <div style='padding:10px; margin:5px 0; background:white;
                                border-radius:8px; border:1px solid #f0f0f0;'>
                        <span class='{badge}'>{log['level'].upper()}</span>
                        &nbsp;<strong>{log['timestamp']}</strong>
                        &nbsp;— {log['message']}
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("📝 Aucun log pour l'instant")

        # ══════════════════════════════════════════════════════════════════
        # TAB 4 — Statistiques
        # ══════════════════════════════════════════════════════════════════
        with tab4:
            st.markdown("### 📈 Statistiques de session")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📤 Uploadés",
                       st.session_state.statistics['total_uploaded'])
            c2.metric("✅ Générés",
                       st.session_state.statistics['total_generated'])
            c3.metric("❌ Erreurs",
                       st.session_state.statistics['total_errors'])
            times = st.session_state.statistics['generation_times']
            avg   = sum(times) / len(times) if times else 0
            c4.metric("⏱️ Temps moy.", f"{avg:.2f}s")

    else:
        # Fichiers uploadés mais tous invalides / doublons
        with tab1:
            st.warning(
                "⚠️ Aucun fichier valide chargé. "
                "Vérifiez vos fichiers ou cliquez sur Réinitialiser."
            )
            if st.session_state.duplicate_files:
                st.info(
                    f"Doublons détectés : "
                    f"{', '.join(st.session_state.duplicate_files)}"
                )

else:
    # Aucun fichier — état initial
    st.markdown("""
    <div style='text-align:center; padding:80px; background:white;
                border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.06);'>
        <p style='font-size:96px; margin:0;'>📁</p>
        <h3 style='color:#667eea; margin:16px 0 8px;'>
            Uploadez vos fichiers JSON/YAML pour commencer
        </h3>
        <p style='color:#888;'>
            Formats supportés : JSON, YAML · Multi-fichiers accepté
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; color:#666; padding:20px;
            border-top:2px solid #e0e0e0; margin-top:20px;'>
    <p>AKAZI Generator v6.1 — Header/Footer Builder intégré 🚀</p>
</div>
""", unsafe_allow_html=True)
