"""
AKAZI Generator - Streamlit Application
Main entry point for the document generation application.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger import get_logger
from utils.cache_manager import init_session_state

logger = get_logger(__name__)


# Page configuration
st.set_page_config(
    page_title="AKAZI Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main application entry point."""
    
    # Initialize session state
    init_session_state()
    
    # Title and introduction
    st.title("📄 AKAZI Document Generator")
    st.markdown("---")
    
    # Welcome message
    st.markdown("""
    ## Bienvenue sur AKAZI Generator ! 👋
    
    Cette application vous permet de générer automatiquement des documents professionnels 
    au format Word (.docx) à partir de fichiers JSON ou YAML.
    
    ### 📋 Formats supportés
    
    - **AKAZI Job Description** (EN/FR) - Fiches de poste professionnelles
    - **AKAZI CV** - CVs au format AKAZI standardisé
    - **MC2I CV** - Dossiers de compétences au format MC2I
    
    ### 🚀 Fonctionnalités
    
    ✅ **Upload multiple** - Traitez plusieurs fichiers en une seule fois  
    ✅ **Auto-détection** - Le type de document est automatiquement détecté  
    ✅ **Multi-formats** - Générez plusieurs formats à partir d'un même fichier source  
    ✅ **Batch processing** - Traitement par lot avec barre de progression  
    ✅ **Continue-on-error** - Le traitement continue même en cas d'erreur  
    ✅ **Download ZIP** - Téléchargez tous vos documents d'un coup  
    ✅ **Dashboard** - Visualisez vos statistiques de génération  
    
    ### 📖 Guide d'utilisation
    
    1. **Naviguez** vers la page "📄 Générateur Batch" dans la sidebar
    2. **Uploadez** vos fichiers JSON/YAML
    3. **Sélectionnez** les formats de sortie souhaités (checkboxes)
    4. **Cliquez** sur "🚀 Générer les documents"
    5. **Téléchargez** vos fichiers individuellement ou en ZIP
    
    ### 📊 Analytics
    
    Consultez la page **Dashboard** pour visualiser :
    - Nombre de documents générés
    - Temps de traitement moyen
    - Taux de succès/échecs
    - Types de documents les plus générés
    
    ### 🔍 Logs & Erreurs
    
    En cas de problème, consultez la page **Logs & Erreurs** pour :
    - Voir les erreurs détaillées
    - Exporter un rapport CSV
    - Débugger les problèmes de génération
    """)
    
    # Quick stats in columns
    st.markdown("---")
    st.subheader("📈 Statistiques rapides")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_generated = st.session_state.get('total_generated', 0)
        st.metric("Documents générés", total_generated)
    
    with col2:
        success_rate = st.session_state.get('success_rate', 100)
        st.metric("Taux de succès", f"{success_rate:.1f}%")
    
    with col3:
        avg_time = st.session_state.get('avg_generation_time', 0)
        st.metric("Temps moyen", f"{avg_time:.2f}s")
    
    with col4:
        errors_count = st.session_state.get('total_errors', 0)
        st.metric("Erreurs", errors_count, delta_color="inverse")
    
    # Getting started guide
    st.markdown("---")
    st.subheader("🎯 Commencer maintenant")
    
    st.info("""
    👈 **Utilisez la sidebar** pour naviguer entre les différentes pages :
    
    - **📄 Générateur Batch** : Page principale pour générer vos documents
    - **📊 Dashboard** : Visualisez vos statistiques détaillées
    - **🔍 Logs & Erreurs** : Consultez les erreurs et logs
    - **⚙️ Configuration** : Paramètres avancés (optionnel)
    """)
    
    # Quick links
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📚 Documentation
        - [README.md](./README.md) - Guide complet
        - [ARCHITECTURE.md](./ARCHITECTURE.md) - Architecture du projet
        - [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) - Guide d'installation
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 Support
        - Consultez les logs en cas d'erreur
        - Vérifiez le format de vos fichiers JSON/YAML
        - Assurez-vous que les champs requis sont présents
        """)
    
    # Footer
    st.markdown("---")
    st.caption("""
    **AKAZI Generator v2.0** | Développé par Jean Jacques | 
    Powered by Streamlit & python-docx
    """)


if __name__ == "__main__":
    main()
