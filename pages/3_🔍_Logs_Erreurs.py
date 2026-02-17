"""
Page: Logs & Erreurs
View logs and errors with CSV export functionality.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io

from utils.cache_manager import get_error_history, get_generation_history
from utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Logs & Erreurs", page_icon="🔍", layout="wide")


def main():
    st.title("🔍 Logs & Erreurs")
    st.markdown("Consultez les erreurs et exportez des rapports détaillés")
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["❌ Erreurs", "📋 Historique complet", "⚙️ Paramètres"])
    
    with tab1:
        display_errors_tab()
    
    with tab2:
        display_history_tab()
    
    with tab3:
        display_settings_tab()


def display_errors_tab():
    """Display errors tab with filtering and export."""
    st.subheader("❌ Erreurs de génération")
    
    errors = get_error_history()
    
    if not errors:
        st.success("✅ Aucune erreur enregistrée ! Tout fonctionne parfaitement.")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        # Filter by doc type
        df = pd.DataFrame(errors)
        if 'doc_type' in df.columns:
            doc_types = ['Tous'] + list(df['doc_type'].unique())
            selected_type = st.selectbox("Filtrer par type", doc_types)
        else:
            selected_type = 'Tous'
    
    with col2:
        # Filter by date
        filter_date = st.date_input("Filtrer par date", value=None)
    
    # Apply filters
    filtered_errors = errors.copy()
    
    if selected_type != 'Tous' and 'doc_type' in df.columns:
        filtered_errors = [e for e in filtered_errors if e.get('doc_type') == selected_type]
    
    if filter_date:
        filtered_errors = [
            e for e in filtered_errors
            if 'timestamp' in e and
            pd.to_datetime(e['timestamp']).date() == filter_date
        ]
    
    # Display count
    st.info(f"📊 {len(filtered_errors)} erreur(s) trouvée(s)")
    
    # Export button
    if filtered_errors:
        csv_data = generate_error_csv(filtered_errors)
        st.download_button(
            label="📥 Exporter en CSV",
            data=csv_data,
            file_name=f"akazi_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Display errors
    for i, error in enumerate(reversed(filtered_errors), 1):
        with st.expander(
            f"❌ Erreur #{i} - {error.get('input_file', 'Unknown')} "
            f"({error.get('doc_type', 'Unknown')})",
            expanded=(i == 1)  # Expand first error
        ):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("**Détails:**")
                st.text(f"Fichier: {error.get('input_file', 'N/A')}")
                st.text(f"Type: {error.get('doc_type', 'N/A')}")
                
                if 'timestamp' in error:
                    timestamp = pd.to_datetime(error['timestamp'])
                    st.text(f"Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                st.markdown("**Message d'erreur:**")
                error_msg = error.get('error_message', 'No error message')
                st.error(error_msg)
                
                # Show stack trace if available
                if 'stack_trace' in error:
                    with st.expander("Stack trace"):
                        st.code(error['stack_trace'])


def display_history_tab():
    """Display complete generation history."""
    st.subheader("📋 Historique complet des générations")
    
    history = get_generation_history()
    
    if not history:
        st.info("🔍 Aucun historique disponible")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(history)
    
    # Format columns
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    if 'success' in df.columns:
        df['Status'] = df['success'].apply(lambda x: '✅ Success' if x else '❌ Error')
    
    if 'generation_time' in df.columns:
        df['Temps (s)'] = df['generation_time'].round(2)
    
    # Select columns to display
    display_cols = []
    for col in ['timestamp', 'input_file', 'output_file', 'doc_type', 'Status', 'Temps (s)']:
        if col in df.columns:
            display_cols.append(col)
    
    # Display table with filters
    st.dataframe(df[display_cols] if display_cols else df, width='stretch', hide_index=True)
    
    # Export button
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exporter l'historique complet (CSV)",
        data=csv_data,
        file_name=f"akazi_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def display_settings_tab():
    """Display log settings and management."""
    st.subheader("⚙️ Paramètres des logs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗑️ Gestion des données")
        
        if st.button("Effacer l'historique des erreurs", type="secondary"):
            if st.session_state.get('error_history'):
                st.session_state['error_history'] = []
                st.success("✅ Historique des erreurs effacé")
                st.rerun()
        
        if st.button("Effacer tout l'historique", type="secondary"):
            if st.session_state.get('generation_history'):
                st.session_state['generation_history'] = []
                st.session_state['error_history'] = []
                st.success("✅ Tout l'historique a été effacé")
                st.rerun()
    
    with col2:
        st.markdown("### 📊 Statistiques")
        
        history = get_generation_history()
        errors = get_error_history()
        
        st.metric("Total générations", len(history))
        st.metric("Total erreurs", len(errors))
        
        if history:
            success_count = sum(1 for h in history if h.get('success', False))
            success_rate = (success_count / len(history)) * 100
            st.metric("Taux de succès", f"{success_rate:.1f}%")


def generate_error_csv(errors: list) -> bytes:
    """Generate CSV export of errors."""
    if not errors:
        return b""
    
    df = pd.DataFrame(errors)
    
    # Select relevant columns
    export_cols = []
    for col in ['timestamp', 'input_file', 'doc_type', 'error_message', 'error_type']:
        if col in df.columns:
            export_cols.append(col)
    
    csv_buffer = io.StringIO()
    df[export_cols].to_csv(csv_buffer, index=False, encoding='utf-8')
    
    return csv_buffer.getvalue().encode('utf-8')


if __name__ == "__main__":
    main()
