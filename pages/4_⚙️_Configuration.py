"""
Page: Configuration
Advanced settings and configuration options (optional).
"""

import streamlit as st
from pathlib import Path

# Imports config avec fallback propre si non disponibles
try:
    from config.base_config import BaseConfig
    from config.akazi_jobdesc_config import AkaziJobDescConfig
    from config.akazi_cv_config import AkaziCVConfig
    from config.mc2i_cv_config import MC2ICVConfig
    CONFIGS_AVAILABLE = True
except Exception:
    CONFIGS_AVAILABLE = False

st.set_page_config(page_title="Configuration", page_icon="⚙️", layout="wide")


def main():
    st.title("⚙️ Configuration")
    st.markdown("Paramètres avancés et préférences de l'application")
    st.markdown("---")
    
    # Tabs for different config sections
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Apparence", "📝 Formats", "💾 Stockage", "📋 Prompts"])
    
    with tab1:
        display_appearance_settings()
    
    with tab2:
        display_format_settings()
    
    with tab3:
        display_storage_settings()

    with tab4:
        display_prompts()


def display_appearance_settings():
    """Display appearance and UI settings."""
    st.subheader("🎨 Paramètres d'apparence")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Interface")
        
        theme = st.radio(
            "Thème de couleur",
            options=["Clair", "Sombre", "Auto"],
            index=2,
            help="Le thème 'Auto' s'adapte aux préférences du système"
        )
        
        show_progress = st.checkbox(
            "Afficher la barre de progression détaillée",
            value=True,
            help="Affiche des informations détaillées pendant la génération"
        )
        
        compact_mode = st.checkbox(
            "Mode compact",
            value=False,
            help="Réduit l'espacement pour afficher plus d'informations"
        )
    
    with col2:
        st.markdown("### Notifications")
        
        show_success_toast = st.checkbox(
            "Notifications de succès",
            value=True,
            help="Affiche une notification lors de la génération réussie"
        )
        
        show_error_toast = st.checkbox(
            "Notifications d'erreur",
            value=True,
            help="Affiche une notification en cas d'erreur"
        )
        
        sound_enabled = st.checkbox(
            "Son de notification",
            value=False,
            help="Joue un son lors des notifications"
        )
    
    if st.button("💾 Enregistrer les préférences"):
        # Save to session state
        st.session_state['theme'] = theme
        st.session_state['show_progress'] = show_progress
        st.session_state['compact_mode'] = compact_mode
        st.session_state['show_success_toast'] = show_success_toast
        st.session_state['show_error_toast'] = show_error_toast
        st.session_state['sound_enabled'] = sound_enabled
        
        st.success("✅ Préférences enregistrées avec succès !")


def display_format_settings():
    """Display document format settings."""
    st.subheader("📝 Paramètres des formats de documents")
    
    # Select format to configure
    format_type = st.selectbox(
        "Sélectionnez le format à configurer",
        options=["AKAZI Job Description", "AKAZI CV", "MC2I CV"]
    )
    
    st.markdown("---")
    
    if format_type == "AKAZI Job Description":
        display_akazi_jobdesc_config()
    elif format_type == "AKAZI CV":
        display_akazi_cv_config()
    elif format_type == "MC2I CV":
        display_mc2i_cv_config()


def display_akazi_jobdesc_config():
    """Display AKAZI Job Description configuration — version statique robuste."""
    st.markdown("### 📄 Configuration AKAZI Job Description")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔤 Polices**")
        st.markdown("""
| Élément | Valeur |
|---------|--------|
| Police principale | Century Gothic |
| Taille corps | 10 pt |
| Taille titres sections | 12 pt |
| Taille titre principal | 14 pt |
""")

    with col2:
        st.markdown("**🎨 Couleurs**")
        st.markdown("""
| Élément | Code couleur |
|---------|-------------|
| Titre principal | 🔴 `#C00000` |
| Budget | 🔴 `#C00000` |
| Texte standard | ⚫ `#000000` |
| Éléments inférés | 🟠 `#FF8C00` |
""")

    st.markdown("**📐 Mise en page**")
    st.markdown("""
| Paramètre | Valeur |
|-----------|--------|
| Marges | 2.54 cm (toutes) |
| Interligne | 1.15 |
| Espace avant titre section | 20 pt |
| Espace après titre section | 6 pt |
| Indentation bullet niveau 1 | 1.0 cm (hanging 0.5 cm) |
| Indentation bullet niveau 2 | 1.5 cm (hanging 0.5 cm) |
""")
    st.info("ℹ️ Configuration définie dans `config/akazi_jobdesc_config.py`")


def display_akazi_cv_config():
    """Display AKAZI CV configuration."""
    st.markdown("### 📋 Configuration AKAZI CV")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔤 Polices**")
        st.markdown("""
| Élément | Valeur |
|---------|--------|
| Police principale | Century Gothic |
| Taille corps | 9 pt |
| Taille en-tête | 11 pt |
""")

    with col2:
        st.markdown("**🎨 Couleurs**")
        st.markdown("""
| Élément | Code couleur |
|---------|-------------|
| En-tête nom | 🔴 `#C00000` |
| Sous-titres | 🔵 `#002060` |
| Email | 🟡 `#CC9900` |
""")

    st.markdown("**📐 Mise en page**")
    st.markdown("""
| Paramètre | Valeur |
|-----------|--------|
| Tableau | 2 colonnes : 21% / 79% |
| Bordures | Visibles |
""")
    st.info("ℹ️ Configuration définie dans `config/akazi_cv_config.py`")


def display_mc2i_cv_config():
    """Display MC2I CV configuration."""
    st.markdown("### 📊 Configuration MC2I CV")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔤 Polices**")
        st.markdown("""
| Élément | Valeur |
|---------|--------|
| Police principale | Lato |
| Taille corps | 10 pt |
| Taille titres mission | 14 pt |
""")

    with col2:
        st.markdown("**🎨 Couleurs**")
        st.markdown("""
| Élément | Code couleur |
|---------|-------------|
| Entreprise | 🩷 `#DD0061` |
| Mission | 🔵 `#006A9E` |
| Texte | ⬛ `#575856` |
""")

    st.markdown("**📐 Structure**")
    st.markdown("""
| Paramètre | Valeur |
|-----------|--------|
| Style titres | Small Caps |
| Séparateurs | Horizontaux entre sections |
| Intro | 4 paragraphes |
""")
    st.info("ℹ️ Configuration définie dans `config/mc2i_cv_config.py`")

def display_storage_settings():
    """Display storage and cache settings."""
    st.subheader("💾 Paramètres de stockage")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗂️ Dossiers de sortie")
        
        output_dir = st.text_input(
            "Dossier de sortie par défaut",
            value="/tmp",
            help="Dossier où les fichiers générés sont sauvegardés temporairement"
        )
        
        auto_cleanup = st.checkbox(
            "Nettoyage automatique",
            value=True,
            help="Supprime automatiquement les fichiers temporaires après téléchargement"
        )
        
        cleanup_delay = st.slider(
            "Délai de nettoyage (heures)",
            min_value=1,
            max_value=24,
            value=24,
            help="Temps avant suppression des fichiers temporaires"
        )
    
    with col2:
        st.markdown("### 📊 Cache et historique")
        
        max_history = st.number_input(
            "Nombre max d'entrées dans l'historique",
            min_value=10,
            max_value=1000,
            value=100,
            help="Limite le nombre d'entrées conservées en mémoire"
        )
        
        cache_enabled = st.checkbox(
            "Activer le cache",
            value=True,
            help="Met en cache les résultats de génération pour améliorer les performances"
        )
        
        if st.button("🗑️ Vider le cache", type="secondary"):
            st.session_state.clear()
            st.success("✅ Cache vidé avec succès !")
            st.rerun()
    
    st.markdown("---")
    
    if st.button("💾 Sauvegarder la configuration"):
        st.session_state['output_dir'] = output_dir
        st.session_state['auto_cleanup'] = auto_cleanup
        st.session_state['cleanup_delay'] = cleanup_delay
        st.session_state['max_history'] = max_history
        st.session_state['cache_enabled'] = cache_enabled
        
        st.success("✅ Configuration sauvegardée avec succès !")



# ============================================================
# PROMPTS TAB
# ============================================================

# Mapping: nom affiché → fichier .md dans config/
PROMPTS_CATALOG = {
    "📄 AKAZI Job Description (FR)": {
        "file": "AKAZI_Job_Description_Generator_Prompt_V1-1__V2026-02-17.md",
        "description": "Prompt pour générer des fiches de poste AKAZI en français",
        "format_code": "JD-AKAZI-FR",
        "lang": "🇫🇷 Français",
    },
    "📄 AKAZI Job Description (EN)": {
        "file": "AKAZI_Job_Description_Generator_Prompt_V1-1__V2026-02-17.md",
        "description": "Prompt for generating AKAZI job descriptions in English",
        "format_code": "JD-AKAZI-EN",
        "lang": "🇬🇧 English",
    },
    "📋 AKAZI CV": {
        "file": "AKAZI_CV_Generator_Prompt_V1.md",
        "description": "Prompt pour générer des CVs au format AKAZI",
        "format_code": "CV-AKAZI",
        "lang": "🇫🇷 Français",
    },
    "📊 MC2I CV": {
        "file": "MC2I_CV_Generator_Prompt_V1.md",
        "description": "Prompt pour générer des CVs au format MC2I",
        "format_code": "CV-MC2I",
        "lang": "🇫🇷 Français",
    },
}


def _load_prompt_file(filename: str) -> str | None:
    """Charge le contenu d'un fichier prompt depuis config/"""
    config_dir = Path(__file__).parent.parent / "config"
    filepath = config_dir / filename
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return None


def _convert_md_to_pdf_bytes(md_content: str, title: str) -> bytes:
    """
    Convertit du Markdown en PDF via HTML → bytes.
    Utilise uniquement des modules stdlib + disponibles sur Streamlit Cloud.
    """
    try:
        import markdown as md_lib
        html_body = md_lib.markdown(
            md_content,
            extensions=["tables", "fenced_code", "nl2br"]
        )
    except ImportError:
        # Fallback minimal si markdown non installé
        html_body = f"<pre>{md_content}</pre>"

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px;
           line-height: 1.6; margin: 40px; color: #222; }}
    h1 {{ color: #002060; border-bottom: 2px solid #667eea; padding-bottom: 8px; }}
    h2 {{ color: #002060; margin-top: 24px; }}
    h3 {{ color: #444; }}
    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px;
            font-family: Consolas, monospace; font-size: 11px; }}
    pre  {{ background: #f4f4f4; padding: 12px; border-radius: 6px;
            overflow-x: auto; font-size: 11px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
    th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
    th {{ background: #667eea; color: white; }}
    blockquote {{ border-left: 4px solid #667eea; margin: 0;
                  padding-left: 16px; color: #555; }}
    .header {{ background: linear-gradient(135deg, #667eea, #764ba2);
               color: white; padding: 20px; border-radius: 8px;
               margin-bottom: 24px; }}
  </style>
</head>
<body>
  <div class="header"><h1 style="color:white; border:none;">{title}</h1>
  <p style="margin:0; opacity:0.85;">AKAZI Generator — Prompt de génération</p></div>
  {html_body}
</body>
</html>"""

    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html).write_pdf()
        return pdf_bytes
    except ImportError:
        # weasyprint non disponible → retourner l'HTML encodé en bytes
        return html.encode("utf-8")


def display_prompts():
    """Onglet Prompts : aperçu + téléchargement MD et PDF"""

    st.subheader("📋 Prompts de génération")
    st.markdown(
        "Ces prompts sont à utiliser avec votre IA (Claude, GPT-4…) pour convertir "
        "un document source (CV, fiche de poste PDF) en fichier **JSON/YAML** "
        "prêt à être injecté dans le générateur."
    )

    st.markdown("---")

    # ── Sélecteur de prompt ──────────────────────────────────────────────────
    selected_name = st.selectbox(
        "Sélectionnez un prompt",
        options=list(PROMPTS_CATALOG.keys()),
        index=0
    )

    prompt_info = PROMPTS_CATALOG[selected_name]
    md_content = _load_prompt_file(prompt_info["file"])

    # ── Métadonnées ──────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Format** : `{prompt_info['format_code']}`")
    with col2:
        st.markdown(f"**Langue** : {prompt_info['lang']}")
    with col3:
        st.markdown(f"**Fichier** : `{prompt_info['file']}`")

    st.markdown(f"_{prompt_info['description']}_")
    st.markdown("---")

    if md_content is None:
        st.error(
            f"❌ Fichier introuvable : `config/{prompt_info['file']}`\n\n"
            "Vérifiez que le fichier existe dans le dossier `config/`."
        )
        return

    # ── Boutons de téléchargement ────────────────────────────────────────────
    stem = Path(prompt_info["file"]).stem
    col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 3])

    with col_dl1:
        st.download_button(
            label="⬇️ Télécharger .md",
            data=md_content.encode("utf-8"),
            file_name=f"{stem}.md",
            mime="text/markdown",
            use_container_width=True,
            key=f"dl_md_{stem}"
        )

    with col_dl2:
        # Générer PDF à la volée
        pdf_or_html = _convert_md_to_pdf_bytes(md_content, selected_name)
        is_pdf = pdf_or_html[:4] == b"%PDF"
        st.download_button(
            label="⬇️ Télécharger PDF" if is_pdf else "⬇️ Télécharger HTML",
            data=pdf_or_html,
            file_name=f"{stem}.{'pdf' if is_pdf else 'html'}",
            mime="application/pdf" if is_pdf else "text/html",
            use_container_width=True,
            key=f"dl_pdf_{stem}"
        )

    # ── Aperçu Markdown ──────────────────────────────────────────────────────
    st.markdown("### 👁️ Aperçu du prompt")

    with st.expander("Afficher / Masquer le prompt complet", expanded=True):
        st.markdown(
            f"""
            <div style="background:#f8f9ff; border:1px solid #dde3ff;
                        border-radius:8px; padding:20px; max-height:600px;
                        overflow-y:auto; font-family: 'Segoe UI', sans-serif;
                        font-size:14px; line-height:1.7;">
            """,
            unsafe_allow_html=True
        )
        st.markdown(md_content)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Instructions d'utilisation ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💡 Comment utiliser ce prompt ?")
    st.info(
        "1. **Téléchargez** le prompt ci-dessus (`.md` ou `.pdf`)\n"
        "2. **Ouvrez** votre IA préférée (Claude, ChatGPT, Gemini…)\n"
        "3. **Copiez-collez** le prompt, puis **joignez** votre document source (PDF du CV ou de la fiche de poste)\n"
        "4. **Récupérez** le JSON/YAML généré par l'IA\n"
        "5. **Uploadez** ce fichier dans le **Générateur Batch** pour produire votre document Word ✅"
    )


if __name__ == "__main__":
    main()
