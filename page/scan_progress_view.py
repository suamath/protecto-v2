import streamlit as st
import pandas as pd
from protectoMethods import ProtectoAPI

class ScanProgressView:
    def __init__(self, protecto_api: ProtectoAPI):
        self.protecto_api = protecto_api

    def render(self):
        st.title("Scan Progress")
        
        # Add refresh button at the top
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("🔄 Refresh", key="refresh_button", use_container_width=True):
                st.rerun()
        
        try:
            progress_data = self.protecto_api.get_scan_progress()
            df = pd.DataFrame(progress_data)
            
            edited_df = self._create_progress_table(df)

        except Exception as e:
            st.error(f"Error displaying progress: {str(e)}")

    def _create_progress_table(self, df: pd.DataFrame) -> pd.DataFrame:
        # Initialize table page in session state if not exists
        if 'progress_table_page' not in st.session_state:
            st.session_state.progress_table_page = 1

        # Pagination settings
        batch_size = 5  # Show 5 items per page
        total_pages = max(1, (len(df) + batch_size - 1) // batch_size)

        # Ensure current page is within valid range
        st.session_state.progress_table_page = min(max(1, st.session_state.progress_table_page), total_pages)

        # Calculate indices
        start_idx = (st.session_state.progress_table_page - 1) * batch_size
        end_idx = min(start_idx + batch_size, len(df))
        
        # Get current page's data
        df_page = df.iloc[start_idx:end_idx].copy()

        # Add styling for the retry button and table layout
        st.markdown("""
            <style>
            .stDataFrame {
                border: 1px solid #f0f2f6;
                border-radius: 4px;
                padding: 1rem 0;
            }
            .pagination-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.5rem;
                margin-top: 0.5rem;
                border-top: 1px solid #f0f2f6;
            }
            .page-info {
                color: #666;
                font-size: 0.9em;
            }
            .retry-button {
                background-color: #ff4b4b;
                color: white;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                font-size: 0.8em;
                cursor: pointer;
                border: none;
                transition: background-color 0.2s;
            }
            .retry-button:hover {
                background-color: #ff3333;
            }
            /* New styles for refresh button alignment */
            .button-container {
                display: flex;
                justify-content: flex-end;
                padding: 0.5rem 0;
                margin-bottom: 1rem;
            }
            .stButton button {
                width: 150px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Configure table columns
        column_config = {
            "request_id": st.column_config.TextColumn(
                "Request ID",
                width="large"
            ),
            "object_name": st.column_config.TextColumn(
                "Object",
                width="medium"
            ), 
            "total_count": st.column_config.NumberColumn(
                "Total Records",
                width="medium"
            ),
            "scanned_count": st.column_config.NumberColumn(
                "Scanned Records",
                width="medium"
            ),
            "status": st.column_config.TextColumn(
                "Status",
                width="small"
            ),
            "last_updated_time": st.column_config.TextColumn(
                "Last Updated",
                width="large"
            )
        }
        
        # Create the data editor
        editor = st.data_editor(
            df_page,
            column_config=column_config,
            disabled=["request_id", "object_name", "total_count", "scanned_count", 
                     "Progress", "status", "last_updated_time"],
            hide_index=True,
            use_container_width=True,
            height=400,
            column_order=["request_id", "object_name", "total_count", "scanned_count", 
                         "status", "last_updated_time"]
        )

        # Update the main dataframe
        df.iloc[start_idx:end_idx] = editor
        
        # Add space between table and buttons
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Show retry buttons for failed status rows
        failed_rows = df_page[df_page['status'] == 'Failed']
        if not failed_rows.empty:
            st.markdown("""
                <style>
                .retry-container {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin-bottom: 8px;
                }
                .request-id {
                    color: #666;
                    font-size: 0.9em;
                }
                </style>
            """, unsafe_allow_html=True)
            
            for _, row in failed_rows.iterrows():
                cols = st.columns([4, 1, 1])
                with cols[1]:
                    if st.button("⟳ Retry", key=f"retry_{row['request_id']}", use_container_width=True):
                        self._handle_retry(row['request_id'])
                with cols[2]:
                    st.markdown(f"<div class='request-id'>ID: {row['request_id']}</div>", unsafe_allow_html=True)
        
        # Add space between retry buttons and pagination
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Create pagination controls
        st.markdown('<div class="pagination-container">', unsafe_allow_html=True)
        
        # Create columns for pagination layout
        info_col, nav_col, page_col = st.columns([2, 2, 1])
        
        with info_col:
            st.markdown(f"""
                <div class="page-info">
                    Showing {start_idx + 1} to {end_idx} of {len(df)} entries
                </div>
            """, unsafe_allow_html=True)
        
        with nav_col:
            cols = st.columns([1, 2, 1])
            
            # Previous button
            if cols[0].button("⬅️", disabled=st.session_state.progress_table_page == 1, key="progress_prev"):
                st.session_state.progress_table_page -= 1
                st.rerun()
            
            # Page info
            cols[1].markdown(f"""
                <div style='text-align: center; color: #666;'>
                    Page {st.session_state.progress_table_page} of {total_pages}
                </div>
            """, unsafe_allow_html=True)
            
            # Next button
            if cols[2].button("➡️", disabled=st.session_state.progress_table_page == total_pages, key="progress_next"):
                st.session_state.progress_table_page += 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return df

    def _handle_page_change(self, change: int):
        st.session_state.progress_table_page += change
        st.rerun()

    def _handle_retry(self, request_id: str):
        """Handle retry action for failed scans"""
        try:
            # Add your retry logic here
            st.success(f"Retrying scan for request ID: {request_id}")
            # You might want to call an API method here
            # self.protecto_api.retry_scan(request_id)
        except Exception as e:
            st.error(f"Error retrying scan: {str(e)}")
