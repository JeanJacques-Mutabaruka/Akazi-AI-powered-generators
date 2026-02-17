"""
Page: Configuration
Advanced settings and configuration options (optional).
"""

import streamlit as st
from pathlib import Path

from config.base_config import BaseConfig
from config.akazi_jobdesc_config import AkaziJobDescConfig
from config.akazi_cv_config import AkaziCVConfig
from config.mc2i_cv_config import MC2ICVConfig

st.set_page_config(page_title="Configuration", page_icon="⚙️", layout="wide")


def main():
    st.title("⚙️ Configuration")
    st.markdown("Paramètres avancés et préférences de l'application")
    st.markdown("---")
    
    # Tabs for different config sections
    tab1, tab2, tab3 = st.tabs(["🎨 Apparence", "📝 Formats", "💾 Stockage"])
    
    with tab1:
        display_appearance_settings()
    
    with tab2:
        display_format_settings()
    
    with tab3:
        display_storage_settings()


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
    """Display AKAZI Job Description configuration."""
    st.markdown("### 📄 Configuration AKAZI Job Description")
    
    config = AkaziJobDescConfig()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Polices**")
        st.text(f"Police principale: {config.fonts['main']['name']}")
        st.text(f"Taille corps: {config.fonts['main']['size_body']} pt")
        st.text(f"Taille titres: {config.fonts['main']['size_title']} pt")
    
    with col2:
        st.markdown("**Couleurs**")
        st.text(f"Noir: #{config.colors['black']}")
        st.text(f"Rouge: #{config.colors['red']}")
        st.text(f"Orange: #{config.colors['orange']}")
    
    st.info("ℹ️ Les configurations sont définies dans `/config/akazi_jobdesc_config.py`")


def display_akazi_cv_config():
    """Display AKAZI CV configuration."""
    st.markdown("### 📋 Configuration AKAZI CV")
    
    st.info("📌 Le format AKAZI CV utilise des spécifications strictes définies dans le prompt de transformation V3")
    
    st.markdown("""
    **Spécifications AKAZI CV:**
    - Police: Century Gothic 9pt (corps), 11pt (en-tête)
    - Couleur rouge: #C00000 (en-tête)
    - Couleur bleue: #002060 (sous-titres)
    - Couleur or: #CC9900 (email)
    - Tableaux avec colonnes 21% / 79%
    - Bordures visibles
    """)


def display_mc2i_cv_config():
    """Display MC2I CV configuration."""
    st.markdown("### 📊 Configuration MC2I CV")
    
    st.info("📌 Le format MC2I utilise les spécifications du prompt de transformation MC2I")
    
    st.markdown("""
    **Spécifications MC2I:**
    - Police: Lato 10pt (corps), 14pt (titres entreprise/mission)
    - Couleur entreprise: #DD0061 (Small Caps)
    - Couleur mission: #006A9E (Small Caps)
    - Couleur texte: #575856
    - Séparateurs horizontaux entre sections
    - 4 paragraphes introductifs
    - Expériences détaillées avec activités et environnement technique
    """)


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


if __name__ == "__main__":
    main()
