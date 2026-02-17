"""
Cache Manager for Streamlit
Manages session state and caching for AKAZI Generator application.
"""

import streamlit as st
from typing import Any, Dict, List, Optional
from datetime import datetime


def init_session_state():
    """
    Initialize Streamlit session state with default values.
    Call this at the start of the application.
    """
    # Generation history
    if 'generation_history' not in st.session_state:
        st.session_state['generation_history'] = []
    
    # Error history
    if 'error_history' not in st.session_state:
        st.session_state['error_history'] = []
    
    # Statistics
    if 'total_generated' not in st.session_state:
        st.session_state['total_generated'] = 0
    
    if 'total_errors' not in st.session_state:
        st.session_state['total_errors'] = 0
    
    if 'success_rate' not in st.session_state:
        st.session_state['success_rate'] = 100.0
    
    if 'avg_generation_time' not in st.session_state:
        st.session_state['avg_generation_time'] = 0.0
    
    # Current session
    if 'session_start_time' not in st.session_state:
        st.session_state['session_start_time'] = datetime.now()
    
    # Uploaded files cache
    if 'uploaded_files_cache' not in st.session_state:
        st.session_state['uploaded_files_cache'] = {}


def cache_generation_result(
    input_file: str,
    output_file: Optional[str],
    doc_type: str,
    success: bool,
    generation_time: float = 0.0,
    error_message: Optional[str] = None
):
    """
    Cache a generation result in session state.
    
    Args:
        input_file: Input filename
        output_file: Output filename (if successful)
        doc_type: Document type generated
        success: Whether generation succeeded
        generation_time: Time taken in seconds
        error_message: Error message if failed
    """
    result = {
        'timestamp': datetime.now().isoformat(),
        'input_file': input_file,
        'output_file': output_file,
        'doc_type': doc_type,
        'success': success,
        'generation_time': generation_time
    }
    
    # Add to generation history
    st.session_state['generation_history'].append(result)
    
    # Update statistics
    if success:
        st.session_state['total_generated'] += 1
    else:
        st.session_state['total_errors'] += 1
        
        # Add to error history
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'input_file': input_file,
            'doc_type': doc_type,
            'error_message': error_message or 'Unknown error',
            'error_type': 'GenerationError'
        }
        st.session_state['error_history'].append(error_record)
    
    # Update success rate
    total = st.session_state['total_generated'] + st.session_state['total_errors']
    if total > 0:
        st.session_state['success_rate'] = (st.session_state['total_generated'] / total) * 100


def get_generation_history() -> List[Dict[str, Any]]:
    """Get complete generation history."""
    return st.session_state.get('generation_history', [])


def get_error_history() -> List[Dict[str, Any]]:
    """Get error history."""
    return st.session_state.get('error_history', [])


def calculate_statistics() -> Dict[str, Any]:
    """
    Calculate current statistics.
    
    Returns:
        Dictionary with statistics
    """
    history = get_generation_history()
    
    # Total counts
    total_generated = st.session_state.get('total_generated', 0)
    total_errors = st.session_state.get('total_errors', 0)
    
    # Success rate
    total = total_generated + total_errors
    success_rate = (total_generated / total * 100) if total > 0 else 100.0
    
    # Average generation time
    successful = [h for h in history if h.get('success', False)]
    times = [h.get('generation_time', 0) for h in successful]
    avg_time = sum(times) / len(times) if times else 0.0
    
    # Today's count
    today = datetime.now().date()
    today_count = sum(
        1 for h in history 
        if datetime.fromisoformat(h['timestamp']).date() == today
    )
    
    return {
        'total_generated': total_generated,
        'total_errors': total_errors,
        'success_rate': success_rate,
        'avg_generation_time': avg_time,
        'today_count': today_count,
        'total_count': total
    }


def update_statistics(
    total_generated: int = 0,
    total_errors: int = 0,
    generation_times: Optional[List[float]] = None
):
    """
    Update statistics in session state.
    
    Args:
        total_generated: Number of successful generations
        total_errors: Number of errors
        generation_times: List of generation times
    """
    if total_generated > 0:
        st.session_state['total_generated'] += total_generated
    
    if total_errors > 0:
        st.session_state['total_errors'] += total_errors
    
    # Update success rate
    total = st.session_state['total_generated'] + st.session_state['total_errors']
    if total > 0:
        st.session_state['success_rate'] = (st.session_state['total_generated'] / total) * 100
    
    # Update average time
    if generation_times:
        current_avg = st.session_state.get('avg_generation_time', 0.0)
        current_count = st.session_state.get('total_generated', 0)
        
        new_avg = sum(generation_times) / len(generation_times)
        
        if current_count > 0:
            # Weighted average
            total_count = current_count + len(generation_times)
            st.session_state['avg_generation_time'] = (
                (current_avg * current_count + new_avg * len(generation_times)) / total_count
            )
        else:
            st.session_state['avg_generation_time'] = new_avg


def clear_cache():
    """Clear all cached data."""
    st.session_state['generation_history'] = []
    st.session_state['error_history'] = []
    st.session_state['total_generated'] = 0
    st.session_state['total_errors'] = 0
    st.session_state['success_rate'] = 100.0
    st.session_state['avg_generation_time'] = 0.0
    st.session_state['uploaded_files_cache'] = {}


def cache_uploaded_file(file_id: str, file_data: Any):
    """Cache an uploaded file."""
    if 'uploaded_files_cache' not in st.session_state:
        st.session_state['uploaded_files_cache'] = {}
    
    st.session_state['uploaded_files_cache'][file_id] = file_data


def get_cached_file(file_id: str) -> Optional[Any]:
    """Get a cached uploaded file."""
    return st.session_state.get('uploaded_files_cache', {}).get(file_id)