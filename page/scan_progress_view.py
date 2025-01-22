import streamlit as st
import pandas as pd
from protectoMethods import ProtectoAPI

class ScanProgressView:
    def __init__(self, protecto_api: ProtectoAPI):
        self.protecto_api = protecto_api

    def render(self):
         # Add spacing control CSS before anything else
         st.markdown("""
             <style>
             .block-container {
                 max-width: 100%;
                 padding-top: 1rem;
                 padding-bottom: 0;
             }
             [data-testid="stAppViewContainer"] {
                 padding-top: 1rem;
             }
             h1 {
                 margin-top: 0 !important;
                 padding-top: 0 !important;
                 margin-bottom: 1rem !important;
             }
             </style>
         """, unsafe_allow_html=True)
     
         # Create title and refresh button in the same row
         col1, col2 = st.columns([5, 1])
         with col1:
             st.markdown('<h1>Scan Progress</h1>', unsafe_allow_html=True)
         with col2:
             if st.button("🔄 Refresh", key="refresh_button", use_container_width=True):
                 progress_data = self.protecto_api.get_scan_progress()
                 st.session_state['scan_data'] = progress_data
                 st.rerun()
     
         self._add_custom_styles()
     
         try:
             self._handle_data_fetch()
             df = pd.DataFrame(st.session_state['scan_data'])
             self._create_progress_table(df)
         except Exception as e:
             st.error(f"Error displaying progress: {str(e)}")

    def _add_custom_styles(self):
        st.markdown("""
            <style>
            .stDataFrame { border: 1px solid #f0f2f6; border-radius: 4px; padding: 0 0; text-align: left !important; }
            .pagination-container { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; margin-top: 0.5rem; border-top: 1px solid #f0f2f6; }
            .page-info { color: #666; font-size: 0.9em; }
            [data-testid="stDataFrameCell"] div:contains("Success") { color: #28a745; font-weight: 500; }
            [data-testid="stDataFrameCell"] div:contains("Failed") { color: #dc3545; font-weight: 500; }
            </style>
        """, unsafe_allow_html=True)

    def _handle_data_fetch(self):
        progress_data = self.protecto_api.get_scan_progress()
        st.session_state['scan_data'] = progress_data

    def _create_progress_table(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'progress_table_page' not in st.session_state:
            st.session_state.progress_table_page = 1

        batch_size = 5
        total_pages = max(1, (len(df) + batch_size - 1) // batch_size)
        st.session_state.progress_table_page = min(max(1, st.session_state.progress_table_page), total_pages)

        start_idx = (st.session_state.progress_table_page - 1) * batch_size
        end_idx = min(start_idx + batch_size, len(df))
        df_page = df.iloc[start_idx:end_idx].copy()
        
        column_config = self._get_column_config()
        
        editor = st.data_editor(
            df_page.style.set_properties(**{'text-align': 'left'}),
            column_config=column_config,
            disabled=["object_name", "criteria", "total_count", "scanned_count", "status", "last_updated_time"],
            hide_index=True,
            use_container_width=True,
            height=400,
            column_order=["object_name", "criteria", "total_count", "scanned_count", "status", "last_updated_time"]
        )
        
        df.iloc[start_idx:end_idx] = editor
        
        self._show_pagination(start_idx, end_idx, len(df), total_pages)
        
        return df

    def _get_column_config(self):
        return {
            "object_name": st.column_config.TextColumn("Object", width="medium"),
            "criteria": st.column_config.TextColumn("Criteria", width="large"),
            "total_count": st.column_config.NumberColumn("Total Records", width="small"),
            "scanned_count": st.column_config.NumberColumn("Scanned Records", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "last_updated_time": st.column_config.TextColumn("Last Updated", width="medium")
        }

    def _show_pagination(self, start_idx, end_idx, total_entries, total_pages):
        st.markdown('<div class="pagination-container">', unsafe_allow_html=True)
        info_col, nav_col, page_col = st.columns([2, 2, 1])
        
        with info_col:
            st.markdown(f'<div class="page-info">Showing {start_idx + 1} to {end_idx} of {total_entries} entries</div>', 
                       unsafe_allow_html=True)
        
        with nav_col:
            self._render_pagination_controls(total_pages)
        
        st.markdown('</div>', unsafe_allow_html=True)

    def _render_pagination_controls(self, total_pages):
        cols = st.columns([1, 2, 1])
        if cols[0].button("⬅️", disabled=st.session_state.progress_table_page == 1, key="progress_prev"):
            st.session_state.progress_table_page -= 1
            st.rerun()
            
        cols[1].markdown(f'<div style="text-align: center; color: #666;">Page {st.session_state.progress_table_page} of {total_pages}</div>', 
                        unsafe_allow_html=True)
            
        if cols[2].button("➡️", disabled=st.session_state.progress_table_page == total_pages, key="progress_next"):
            st.session_state.progress_table_page += 1
            st.rerun()