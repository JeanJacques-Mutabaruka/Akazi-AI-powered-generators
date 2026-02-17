"""
Page: Dashboard
Analytics and statistics dashboard with Plotly visualizations.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

from utils.cache_manager import (
    get_generation_history,
    get_error_history,
    calculate_statistics
)

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")


def main():
    st.title("📊 Dashboard & Analytics")
    st.markdown("Visualisez vos statistiques de génération en temps réel")
    st.markdown("---")
    
    # Get data from session state
    history = get_generation_history()
    errors = get_error_history()
    stats = calculate_statistics()
    
    if not history:
        st.info("🔍 Aucune donnée disponible. Générez des documents pour voir les statistiques.")
        st.stop()
    
    # Key metrics row
    st.subheader("📈 Métriques clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total documents",
            stats.get('total_generated', 0),
            delta=f"+{stats.get('today_count', 0)} aujourd'hui"
        )
    
    with col2:
        success_rate = stats.get('success_rate', 0)
        st.metric(
            "Taux de succès",
            f"{success_rate:.1f}%",
            delta=f"{success_rate - 95:.1f}%" if success_rate < 95 else None
        )
    
    with col3:
        avg_time = stats.get('avg_generation_time', 0)
        st.metric(
            "Temps moyen",
            f"{avg_time:.2f}s",
            delta="-0.5s" if avg_time < 5 else "+0.5s",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Erreurs totales",
            stats.get('total_errors', 0),
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Documents par type")
        plot_documents_by_type(history)
    
    with col2:
        st.subheader("⏱️ Temps de génération par type")
        plot_generation_times(history)
    
    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Historique de génération (7 derniers jours)")
        plot_generation_timeline(history)
    
    with col2:
        st.subheader("❌ Types d'erreurs")
        plot_error_distribution(errors)
    
    # Recent activity table
    st.markdown("---")
    st.subheader("🕒 Activité récente (20 derniers)")
    display_recent_activity(history)


def plot_documents_by_type(history: list):
    """Plot pie chart of documents by type."""
    if not history:
        st.info("Aucune donnée")
        return
    
    df = pd.DataFrame(history)
    
    if 'doc_type' not in df.columns:
        st.info("Aucune donnée de type disponible")
        return
    
    type_counts = df['doc_type'].value_counts().reset_index()
    type_counts.columns = ['Type', 'Count']
    
    fig = px.pie(
        type_counts,
        values='Count',
        names='Type',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)


def plot_generation_times(history: list):
    """Plot bar chart of average generation times by type."""
    if not history:
        st.info("Aucune donnée")
        return
    
    df = pd.DataFrame(history)
    
    if 'doc_type' not in df.columns or 'generation_time' not in df.columns:
        st.info("Aucune donnée de temps disponible")
        return
    
    # Filter successful generations only
    df = df[df['success'] == True]
    
    avg_times = df.groupby('doc_type')['generation_time'].mean().reset_index()
    avg_times.columns = ['Type', 'Avg Time (s)']
    
    fig = px.bar(
        avg_times,
        x='Type',
        y='Avg Time (s)',
        color='Type',
        text_auto='.2f'
    )
    
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def plot_generation_timeline(history: list):
    """Plot timeline of generations over last 7 days."""
    if not history:
        st.info("Aucune donnée")
        return
    
    df = pd.DataFrame(history)
    
    if 'timestamp' not in df.columns:
        st.info("Aucune donnée temporelle disponible")
        return
    
    # Convert timestamp to datetime
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    # Filter last 7 days
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    df = df[df['date'] >= week_ago]
    
    # Count by date and success/failure
    daily_counts = df.groupby(['date', 'success']).size().reset_index(name='count')
    
    fig = px.bar(
        daily_counts,
        x='date',
        y='count',
        color='success',
        barmode='stack',
        labels={'success': 'Status', 'count': 'Documents', 'date': 'Date'},
        color_discrete_map={True: 'green', False: 'red'}
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_error_distribution(errors: list):
    """Plot distribution of error types."""
    if not errors:
        st.info("✅ Aucune erreur enregistrée")
        return
    
    df = pd.DataFrame(errors)
    
    if 'error_type' not in df.columns:
        # Try to extract error type from error message
        if 'error_message' in df.columns:
            df['error_type'] = df['error_message'].apply(lambda x: x.split(':')[0] if ':' in str(x) else 'Unknown')
        else:
            st.info("Aucune donnée d'erreur disponible")
            return
    
    error_counts = df['error_type'].value_counts().reset_index()
    error_counts.columns = ['Error Type', 'Count']
    
    fig = px.bar(
        error_counts,
        x='Count',
        y='Error Type',
        orientation='h',
        color='Count',
        color_continuous_scale='Reds'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_recent_activity(history: list):
    """Display recent activity table."""
    if not history:
        st.info("Aucune activité récente")
        return
    
    # Get last 20 items
    recent = history[-20:][::-1]  # Reverse to show newest first
    
    df = pd.DataFrame(recent)
    
    # Select columns to display
    display_cols = []
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_cols.append('timestamp')
    
    if 'input_file' in df.columns:
        display_cols.append('input_file')
    
    if 'doc_type' in df.columns:
        display_cols.append('doc_type')
    
    if 'success' in df.columns:
        df['status'] = df['success'].apply(lambda x: '✅ Success' if x else '❌ Error')
        display_cols.append('status')
    
    if 'generation_time' in df.columns:
        df['time (s)'] = df['generation_time'].round(2)
        display_cols.append('time (s)')
    
    if display_cols:
        st.dataframe(df[display_cols], width='stretch', hide_index=True)
    else:
        st.info("Colonnes de données insuffisantes")


if __name__ == "__main__":
    main()
