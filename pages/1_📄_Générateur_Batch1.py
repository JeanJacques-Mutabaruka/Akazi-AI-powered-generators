"""
AKAZI Générateur Batch V5 ULTRA FINAL
CORRECTIONS: Formats basés sur document_type ET format_code
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
import yaml
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

st.set_page_config(
    page_title="AKAZI Generator",
    page_icon="📄",
    layout="wide"
)

# CSS (unchanged)
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px; border-radius: 15px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        text-align: center;
    }
    .main-header h1 {margin: 0; font-size: 36px; font-weight: 700;}
    .upload-section {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin-bottom: 30px;
        border-left: 5px solid #667eea;
    }
    .stTabs [data-baseweb="tab-list"] {gap: 10px; padding: 0;}
    .stTabs [data-baseweb="tab"] {
        height: 60px; background: white; border-radius: 10px 10px 0 0;
        padding: 15px 25px; font-weight: 600; font-size: 15px;
        border: 2px solid #e0e0e0; border-bottom: none; transition: all 0.3s;
    }
    .stTabs [data-baseweb="tab"]:nth-child(1) {background: linear-gradient(135deg, #667eea50 0%, #764ba250 100%); color: #667eea;}
    .stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
        transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .stTabs [data-baseweb="tab"]:nth-child(2) {background: linear-gradient(135deg, #11998e50 0%, #38ef7d50 100%); color: #11998e;}
    .stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white;
        transform: translateY(-2px); box-shadow: 0 4px 12px rgba(17, 153, 142, 0.4);
    }
    .stTabs [data-baseweb="tab"]:nth-child(3) {background: linear-gradient(135deg, #f093fb50 0%, #f5576c50 100%); color: #f093fb;}
    .stTabs [data-baseweb="tab"]:nth-child(3)[aria-selected="true"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;
        transform: translateY(-2px); box-shadow: 0 4px 12px rgba(240, 147, 251, 0.4);
    }
    .stTabs [data-baseweb="tab"]:nth-child(4) {background: linear-gradient(135deg, #4facfe50 0%, #00f2fe50 100%); color: #4facfe;}
    .stTabs [data-baseweb="tab"]:nth-child(4)[aria-selected="true"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;
        transform: translateY(-2px); box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
    }
    .badge-success {background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;}
    .badge-error {background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;}
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 12px 30px;
        font-size: 16px; font-weight: 600; border-radius: 10px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# CONFIG
ALL_POSSIBLE_FORMATS = ['JD-AKAZI-FR', 'JD-AKAZI-EN', 'CV-AKAZI', 'CV-MC2I']

def get_available_formats(document_type: str, format_code: str, language_iso: str = None) -> List[str]:
    """
    Détermine les formats ÉLIGIBLES basés sur document_type, format_code ET language_iso.
    
    Pour les JD: la langue source détermine les formats éligibles:
      - FRA → seulement JD-AKAZI-FR (JD-AKAZI-EN = N/A)
      - ENG → seulement JD-AKAZI-EN (JD-AKAZI-FR = N/A)
      - Aucune langue → les deux sont éligibles
    """
    if not document_type or not format_code:
        return []

    # Job Descriptions
    if document_type == "job_description":
        if "AKAZI" in format_code:
            lang = (language_iso or '').upper()
            if lang == 'FRA':
                return ["JD-AKAZI-FR"]          # EN non éligible
            elif lang == 'ENG':
                return ["JD-AKAZI-EN"]          # FR non éligible
            else:
                return ["JD-AKAZI-FR", "JD-AKAZI-EN"]  # Pas de restriction
        return []

    # CVs
    elif document_type == "cv":
        if format_code == "AKAZI_V1":
            return ["CV-AKAZI"]
        elif format_code == "MC2I_V1":
            return ["CV-MC2I"]
        return []

    return []

DOCUMENT_TYPE_NAMES = {"cv": "CV", "job_description": "JD"}
LANGUAGE_NAMES = {"FRA": "FR", "ENG": "EN", "ESP": "ES", "DEU": "DE"}

# SESSION STATE
def init_session_state():
    if 'files_data' not in st.session_state:
        st.session_state.files_data = []
    if 'generated_documents' not in st.session_state:
        st.session_state.generated_documents = {}
    if 'processing_logs' not in st.session_state:
        st.session_state.processing_logs = []
    if 'statistics' not in st.session_state:
        st.session_state.statistics = {
            'total_uploaded': 0,
            'total_generated': 0,
            'total_errors': 0,
            'generation_times': []
        }
    if 'selections' not in st.session_state:
        st.session_state.selections = {}
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0  # ✅ Clé dynamique pour vider le file_uploader

def reset_all():
    """Réinitialise complètement la session"""
    for key in ['files_data', 'generated_documents', 'processing_logs',
                'statistics', 'selections', 'last_files_hash']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.uploader_key += 1  # ✅ Incrémenter → recrée le widget vide
    init_session_state()

init_session_state()

# FUNCTIONS
def load_file_data(uploaded_file) -> Optional[Dict]:
    try:
        content = uploaded_file.read()
        uploaded_file.seek(0)
        if uploaded_file.name.endswith('.json'):
            return json.loads(content)
        elif uploaded_file.name.endswith(('.yaml', '.yml')):
            return yaml.safe_load(content)
    except Exception as e:
        add_log('error', f"Erreur: {uploaded_file.name}: {str(e)}")
    return None

def extract_metadata(data: Dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract metadata from document with fallback for old formats
    Returns: (document_type, format_code, language_iso)
    """
    try:
        # New format: document_metadata
        if 'document_metadata' in data:
            metadata = data['document_metadata']
            return (
                metadata.get('document_type'),
                metadata.get('format_code'),
                metadata.get('language_iso')
            )
        
        # Old format: Format_sortie (backward compatibility)
        if 'Format_sortie' in data:
            format_sortie = data['Format_sortie']
            # Try to infer from Format_sortie
            if 'JD' in format_sortie or 'job' in format_sortie.lower():
                doc_type = 'job_description'
            elif 'CV' in format_sortie:
                doc_type = 'cv'
            else:
                doc_type = None
            
            # Extract format code
            if 'AKAZI' in format_sortie:
                format_code = 'AKAZI_V1'
            elif 'MC2I' in format_sortie:
                format_code = 'MC2I_V1'
            else:
                format_code = None
            
            # Extract language
            if 'FR' in format_sortie or 'FRA' in format_sortie:
                language_iso = 'FRA'
            elif 'EN' in format_sortie or 'ENG' in format_sortie:
                language_iso = 'ENG'
            else:
                language_iso = None
            
            add_log('warning', f"⚠️ Old format detected: 'Format_sortie'. Consider updating to 'document_metadata'.")
            return (doc_type, format_code, language_iso)
        
        # No metadata found
        add_log('error', f"❌ No metadata found. Expected 'document_metadata' or 'Format_sortie'.")
        return (None, None, None)
        
    except Exception as e:
        add_log('error', f"❌ Error extracting metadata: {str(e)}")
        return (None, None, None)

def add_log(level: str, message: str):
    st.session_state.processing_logs.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'level': level,
        'message': message
    })

def generate_document(file_data: Dict, output_format: str, filename: str) -> Optional[bytes]:
    if not GENERATORS_AVAILABLE:
        add_log('error', "Générateurs non disponibles")
        return None
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_input:
            json.dump(file_data, tmp_input)
            input_path = Path(tmp_input.name)
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_output:
            output_path = Path(tmp_output.name)
        
        try:
            if output_format == "CV-AKAZI":
                generator = AkaziCVGenerator(input_path, output_path)
            elif output_format == "CV-MC2I":
                generator = MC2ICVGenerator(input_path, output_path)
            elif output_format in ["JD-AKAZI-FR", "JD-AKAZI-EN"]:
                lang = 'fr' if 'FR' in output_format else 'en'
                generator = AkaziJobDescGenerator(input_path, output_path, lang=lang)
            else:
                add_log('error', f"Format inconnu: {output_format}")
                return None
            
            generator.generate()
            
            with open(output_path, 'rb') as f:
                doc_bytes = f.read()
            
            add_log('success', f"✅ {filename} → {output_format}")
            return doc_bytes
            
        finally:
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
            
    except Exception as e:
        add_log('error', f"❌ {filename}: {str(e)}")
        traceback.print_exc()
        return None

# HEADER
st.markdown("""
<div class="main-header">
    <h1>📄 Générateur Batch AKAZI</h1>
    <p>V5 ULTRA FINAL • Formats Corrigés (CV vs JD)</p>
</div>
""", unsafe_allow_html=True)

# BOUTON RESET
col_r1, col_r2, col_r3 = st.columns([3, 1, 3])
with col_r2:
    if st.button("🔄 Réinitialiser", use_container_width=True, type="secondary"):
        reset_all()
        st.rerun()

# UPLOAD
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown("### 📁 Upload de Fichiers JSON/YAML")

uploaded_files = st.file_uploader(
    "Sélectionnez vos fichiers",
    type=['json', 'yaml', 'yml'],
    accept_multiple_files=True,
    label_visibility="collapsed",
    key=f"file_uploader_{st.session_state.uploader_key}"  # ✅ Clé dynamique → vide au reset
)

st.markdown('</div>', unsafe_allow_html=True)

# PROCESSING
if uploaded_files:
    # Créer un hash unique pour les fichiers actuels
    import hashlib
    current_files_hash = hashlib.md5(
        ''.join([f.name + str(f.size) for f in uploaded_files]).encode()
    ).hexdigest()
    
    # Comparer avec le hash précédent pour détecter changements
    if 'last_files_hash' not in st.session_state or st.session_state.last_files_hash != current_files_hash:
        st.session_state.files_data = []
        st.session_state.last_files_hash = current_files_hash

        # ── Point 3: détecter doublons de stem ──────────────────────────────
        seen_stems: Dict[str, int] = {}
        # Ensemble des content_hash déjà chargés (évite doublons en mémoire)
        existing_content_hashes = {
            f['content_hash'] for f in st.session_state.files_data
        }

        for idx, uploaded_file in enumerate(uploaded_files, 1):
            try:
                data = load_file_data(uploaded_file)
                if not data:
                    st.error(f"❌ Impossible de lire {uploaded_file.name}")
                    continue

                # ── Point 1: vérifier si ce contenu est déjà en mémoire ──
                import hashlib
                content_hash = hashlib.md5(
                    json.dumps(data, sort_keys=True).encode()
                ).hexdigest()

                if content_hash in existing_content_hashes:
                    add_log('warning', f"⚠️ Ignoré (déjà chargé): {uploaded_file.name}")
                    continue  # Fichier identique déjà présent → on skip

                existing_content_hashes.add(content_hash)

                doc_type, format_code, language_iso = extract_metadata(data)

                if not doc_type or not format_code:
                    st.warning(f"⚠️ {uploaded_file.name}: Métadonnées manquantes ou invalides")
                    st.info("""
                    **Structure attendue:**
                    ```yaml
                    document_metadata:
                      document_type: "job_description"  # ou "cv"
                      format_code: "AKAZI_V1"          # ou "MC2I_V1"
                      language_iso: "FRA"              # ou "ENG"
                    ```
                    """)

                # ── Formats éligibles (avec language_iso pour les JD) ──
                available = get_available_formats(doc_type, format_code, language_iso)

                # ── Gestion du stem pour doublons ──
                raw_stem = Path(uploaded_file.name).stem
                if raw_stem in seen_stems:
                    seen_stems[raw_stem] += 1
                    internal_stem = f"{raw_stem}_{seen_stems[raw_stem]}"
                else:
                    seen_stems[raw_stem] = 0
                    internal_stem = raw_stem

                # ── Clé unique robuste: stem interne + idx ──
                file_hash = hashlib.md5(f"{idx}_{internal_stem}".encode()).hexdigest()[:8]

                st.session_state.files_data.append({
                    'id': idx,
                    'filename': uploaded_file.name,
                    'stem': raw_stem,
                    'file_hash': file_hash,
                    'content_hash': content_hash,   # ✅ Pour détecter doublons futurs
                    'type': DOCUMENT_TYPE_NAMES.get(doc_type, '?'),
                    'format': format_code or 'N/A',
                    'lang': LANGUAGE_NAMES.get(language_iso, language_iso or '?'),
                    'language_iso': language_iso or '',
                    'available_outputs': available,
                    'data': data
                })

            except Exception as e:
                st.error(f"❌ Erreur lors du traitement de {uploaded_file.name}: {str(e)}")
                add_log('error', f"Error processing {uploaded_file.name}: {str(e)}")
                traceback.print_exc()
                continue

        add_log('info', f"{len(uploaded_files)} fichier(s) uploadé(s)")
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs([
        "📂 Fichiers Uploadés",
        "📄 Fichiers de Sortie",
        "📊 Rapport",
        "📈 Stats"
    ])
    
    # TAB 1
    with tab1:
        st.markdown("### 📋 Fichiers Uploadés")
        
        if st.session_state.files_data:
            # BOUTONS Sélectionner tout / Déselectionner tout
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                if st.button("☑️ Sélectionner tout", use_container_width=True):
                    for file_info in st.session_state.files_data:
                        for fmt in file_info['available_outputs']:
                            key = f"{file_info['id']}_{fmt}_{file_info['file_hash']}"
                            st.session_state.selections[key] = True
                    st.rerun()
            
            with col2:
                if st.button("☐ Déselectionner tout", use_container_width=True):
                    st.session_state.selections = {}
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Préparer données pour data_editor avec colonnes de sélection
            table_data = []

            for file_info in st.session_state.files_data:
                row = {
                    '#': file_info['id'],
                    'Fichier': file_info['filename'],
                    'Type': file_info['type'],
                    'Format': file_info['format'],
                    'Langue': file_info['lang'],
                }

                available_formats = file_info['available_outputs']
                file_hash = file_info['file_hash']

                for fmt in ALL_POSSIBLE_FORMATS:
                    if fmt in available_formats:
                        # Format éligible → checkbox
                        key = f"{file_info['id']}_{fmt}_{file_hash}"
                        row[fmt] = st.session_state.selections.get(key, False)
                    else:
                        # Format NON éligible → "N/A" (string, non cliquable)
                        row[fmt] = "N/A"

                table_data.append(row)
            
            # Créer DataFrame
            import pandas as pd
            df = pd.DataFrame(table_data)
            
            # Configuration des colonnes
            column_config = {
                '#': st.column_config.NumberColumn('#', width='small'),
                'Fichier': st.column_config.TextColumn('Fichier', width='large'),
                'Type': st.column_config.TextColumn('Type', width='small'),
                'Format': st.column_config.TextColumn('Format', width='small'),
                'Langue': st.column_config.TextColumn('Langue', width='small'),
                'JD-AKAZI-FR': st.column_config.CheckboxColumn('🇫🇷 JD FR', help='Job Description AKAZI Français', width='small'),
                'JD-AKAZI-EN': st.column_config.CheckboxColumn('🇬🇧 JD EN', help='Job Description AKAZI English', width='small'),
                'CV-AKAZI': st.column_config.CheckboxColumn('📄 CV AKAZI', help='CV format AKAZI', width='small'),
                'CV-MC2I': st.column_config.CheckboxColumn('📊 CV MC2I', help='CV format MC2I', width='small'),
            }
            
            # Créer liste des colonnes disabled DYNAMIQUEMENT par ligne
            # Malheureusement st.data_editor ne supporte pas disabled par cellule
            # WORKAROUND: On va gérer ça manuellement après l'édition
            
            # Afficher data editor
            edited_df = st.data_editor(
                df,
                column_config=column_config,
                disabled=['#', 'Fichier', 'Type', 'Format', 'Langue'],
                hide_index=True,
                width='stretch',  # ✅ Utilise 'stretch' au lieu de None
                key=f"data_editor_{st.session_state.get('last_files_hash', '')[:8]}"
            )
            
            # Mettre à jour selections depuis edited_df
            for file_info in st.session_state.files_data:
                available_formats = file_info['available_outputs']
                file_hash = file_info['file_hash']

                for fmt in ALL_POSSIBLE_FORMATS:
                    key = f"{file_info['id']}_{fmt}_{file_hash}"
                    if fmt in available_formats and fmt in edited_df.columns:
                        val = edited_df.loc[edited_df['#'] == file_info['id'], fmt]
                        checkbox_value = val.iloc[0] if not val.empty else False
                        # Ignorer "N/A" ou None
                        if checkbox_value == "N/A" or checkbox_value is None:
                            st.session_state.selections[key] = False
                        else:
                            st.session_state.selections[key] = bool(checkbox_value)
                    else:
                        # Non éligible → forcer False
                        st.session_state.selections[key] = False
            
            # CSS pour griser visuellement les cases non disponibles
            st.markdown("""
            <style>
                /* Rendre les cellules checkbox disabled visuellement */
                .stDataFrame [data-testid="column"] input[type="checkbox"]:disabled {
                    opacity: 0.3;
                    cursor: not-allowed;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # BOUTON GENERATION
            st.markdown("<br>", unsafe_allow_html=True)
            total_selected = sum(1 for v in st.session_state.selections.values() if v)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    f"🚀 Générer ({total_selected} sélectionné(s))",
                    disabled=(total_selected == 0 or not GENERATORS_AVAILABLE),
                    use_container_width=True
                ):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    generated_count = 0
                    error_count = 0
                    tasks = []

                    # Construire tasks avec MÊME logique de key que checkboxes
                    for file_info in st.session_state.files_data:
                        for fmt in file_info['available_outputs']:
                            key = f"{file_info['id']}_{fmt}_{file_info['file_hash']}"
                            if st.session_state.selections.get(key):
                                tasks.append((file_info, fmt))

                    # ── Point 2: timestamp unique pour cette session de génération
                    generation_ts = datetime.now().strftime("%Y-%m-%d %H%M%S")

                    # ── Point 3: détecter doublons de noms de sortie dans cette session
                    output_name_counts: Dict[str, int] = {}

                    for idx, (file_info, fmt) in enumerate(tasks):
                        status_text.text(f"Génération {idx+1}/{len(tasks)}: {file_info['filename']} → {fmt}")
                        progress_bar.progress((idx + 1) / len(tasks))

                        start_time = datetime.now()
                        doc_bytes = generate_document(file_info['data'], fmt, file_info['filename'])
                        elapsed = (datetime.now() - start_time).total_seconds()

                        if doc_bytes:
                            # ── Construire le nom de sortie ──
                            # Base: stem ORIGINAL (sans dédoublonnage dans le nom)
                            # Le (1) va à la fin, après le timestamp, avant .docx
                            base_name = f"{file_info['stem']}_{fmt}__V{generation_ts}"

                            # Détecter si ce base_name a déjà été produit dans cette génération
                            if base_name in output_name_counts:
                                output_name_counts[base_name] += 1
                                # ✅ (1) à la fin, avant l'extension
                                output_filename = f"{base_name} ({output_name_counts[base_name]}).docx"
                            else:
                                output_name_counts[base_name] = 0
                                output_filename = f"{base_name}.docx"

                            # ── Clé download unique: id + fmt + hash + idx ──
                            dl_key = f"dl_{file_info['id']}_{fmt}_{file_info['file_hash']}_{idx}"

                            # ✅ DICT: dl_key en clé → pas de doublons même après rerun
                            st.session_state.generated_documents[dl_key] = {
                                'filename': output_filename,
                                'format': fmt,
                                'data': doc_bytes,
                                'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                'dl_key': dl_key
                            }
                            st.session_state.statistics['generation_times'].append(elapsed)
                            generated_count += 1
                        else:
                            error_count += 1
                    
                    st.session_state.statistics['total_generated'] += generated_count
                    st.session_state.statistics['total_errors'] += error_count
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    if generated_count > 0:
                        st.success(f"✅ {generated_count} document(s) généré(s) !")
                    if error_count > 0:
                        st.error(f"❌ {error_count} erreur(s)")
                    
                    st.rerun()
    
    # TAB 2-4 (unchanged)
    with tab2:
        st.markdown("### 📥 Documents Générés")
        
        if st.session_state.generated_documents:
            for doc in st.session_state.generated_documents.values():  # ✅ .values() sur le dict
                col1, col2, col3 = st.columns([4, 2, 1])
                with col1:
                    st.markdown(f"**{doc['filename']}**")
                with col2:
                    st.markdown(f"<span class='badge-success'>{doc['format']}</span>", unsafe_allow_html=True)
                with col3:
                    st.download_button(
                        "⬇️",
                        data=doc['data'],
                        file_name=doc['filename'],
                        mime=doc['mime_type'],
                        key=doc['dl_key']
                    )

            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📦 Télécharger ZIP", use_container_width=True):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for doc in st.session_state.generated_documents.values():  # ✅ .values()
                            zip_file.writestr(doc['filename'], doc['data'])

                    zip_buffer.seek(0)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                    st.download_button(
                        "⬇️ Télécharger",
                        data=zip_buffer.getvalue(),
                        file_name=f"Documents_AKAZI_{timestamp}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
        else:
            st.info("📭 Aucun document généré")
    
    with tab3:
        st.markdown("### 📊 Logs")
        
        if st.session_state.processing_logs:
            for log in reversed(st.session_state.processing_logs[-30:]):
                badge = 'badge-success' if log['level'] in ['info', 'success'] else 'badge-error'
                st.markdown(f"""
                <div style='padding: 10px; margin: 5px 0; background: white; border-radius: 8px;'>
                    <span class='{badge}'>{log['level'].upper()}</span>
                    <strong>{log['timestamp']}</strong> - {log['message']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📝 Aucun log")
    
    with tab4:
        st.markdown("### 📈 Statistiques")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📤 Uploadés", st.session_state.statistics['total_uploaded'])
        with col2:
            st.metric("✅ Générés", st.session_state.statistics['total_generated'])
        with col3:
            st.metric("❌ Erreurs", st.session_state.statistics['total_errors'])
        with col4:
            times = st.session_state.statistics['generation_times']
            avg = sum(times) / len(times) if times else 0
            st.metric("⏱️ Temps Moy.", f"{avg:.2f}s")

else:
    st.markdown("""
    <div style='text-align: center; padding: 80px; background: white; border-radius: 15px;'>
        <p style='font-size: 96px; margin: 0;'>📁</p>
        <h3 style='color: #667eea;'>Aucun fichier uploadé</h3>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px; border-top: 2px solid #e0e0e0;'>
    <p>AKAZI Generator v5.0 ULTRA FINAL 🚀</p>
</div>
""", unsafe_allow_html=True)
