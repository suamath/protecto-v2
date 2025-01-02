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
                # Fetch fresh data
                progress_data = self.protecto_api.get_scan_progress()
                st.session_state['scan_data'] = progress_data
                st.rerun()
        
        try:
            # Always fetch fresh data if not coming from retry
            if 'is_retry' not in st.session_state or not st.session_state['is_retry']:
                progress_data = self.protecto_api.get_scan_progress()
                st.session_state['scan_data'] = progress_data
            else:
                # Reset retry flag
                st.session_state['is_retry'] = False
            
            df = pd.DataFrame(st.session_state['scan_data'])
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
        
        # Add error message for failed status
        df_page.loc[df_page['status'] == 'Failed', 'error'] = '❌ Timeout Error'
        
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
            .retry-section {
                margin: 1rem 0;
                padding: 0.5rem;
                border-top: 1px solid #f0f2f6;
            }
            .retry-row {
                display: flex;
                align-items: center;
                margin: 0.5rem 0;
                padding: 0.5rem;
                background: #f8f9fa;
                border-radius: 4px;
            }
            .retry-button {
                min-width: 120px;
            }
            .retry-info {
                margin-left: 1rem;
                color: #666;
                font-size: 0.9em;
            }
            /* Status column styling */
            [data-testid="stDataFrameCell"] div:contains("Success") {
                color: #28a745;
                font-weight: 500;
            }
            [data-testid="stDataFrameCell"] div:contains("Failed") {
                color: #dc3545;
                font-weight: 500;
            }
            [data-testid="stDataFrameCell"] div:contains("Retrying") {
                color: #ffc107;
                font-weight: 500;
            }
            /* Error column styling */
            [data-testid="stDataFrameCell"] div:contains("❌") {
                color: #dc3545;
                font-weight: 500;
            }
            </style>
        """, unsafe_allow_html=True)

        # Configure table columns
        column_config = {
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
            ),
            "error": st.column_config.TextColumn(
                "Error",
                width="large",
                help="Error details if scan failed"
            ),
            "retry": st.column_config.CheckboxColumn(    # st.column_config.CheckboxColumn("Selected", width="medium")
                "Retry",
                width="medium"
            )
        }
        #if 'retry'  in df.columns:
        
        
        # Create the data editor
        editor = st.data_editor(
            df_page,
            column_config=column_config,
            disabled=["object_name", "total_count", "scanned_count", 
                     "status", "last_updated_time", "error"],
            hide_index=True,
            use_container_width=True,
            height=400,
            column_order=["retry","object_name", "total_count", "scanned_count", 
                         "status", "last_updated_time", "error"]
        )

        # Update the main dataframe
        df.iloc[start_idx:end_idx] = editor
        
        # Add space between table and buttons
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Show retry buttons for failed status rows
        failed_rows = df_page[df_page['status'] == 'Failed']
        if not failed_rows.empty:
            st.markdown("<div class='retry-section'>", unsafe_allow_html=True)
            retry_request=[]
            
            for _, row in failed_rows.iterrows():
               retry_request.append(row['request_id'])
            st.session_state['retry'] = retry_request   

            cols = st.columns([2, 4, 4])

            with cols[0]:
                    if st.button("Retry Scan", 
                               type="primary",
                               use_container_width=True):
                        self._handle_retry(st.session_state['retry'])

           
            # with cols[1]:
            #     st.markdown(f"""
            #         <div class='retry-info'>
            #             <strong>Request ID:</strong> {row['request_id']}<br>
            #             <strong>Object:</strong> {row['object_name']}
            #         </div>
            #     """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
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
            # Show success toast immediately
            st.toast("Retry request is submitted", icon="✅")
            
            # Get current data
            current_data = st.session_state.get('scan_data', [])
            
            # Find the record to retry
            retry_record = next((record for record in current_data if record['request_id'] == request_id), None)
            
            if retry_record:
                # Prepare data for retry
                selected_object = retry_record['object_name']
                
                # Call API to retry the scan
                save_result = self.protecto_api.insert_or_update_scan_metadata(selected_object, [])
                
                if save_result.get('is_scan_submitted'):
                    st.success("Fields saved successfully!", icon="✅")
                    
                    scan_result = self.protecto_api.submit_to_scan([])
                    if scan_result.get('is_scan_submitted'):
                        st.success("Scan initiated successfully!", icon="✅")
                        
                        # Update the status in the current data
                        retry_record['status'] = 'Retrying'
                        retry_record['error'] = ''  # Clear error message
                        
                        # Get updated data from API
                        updated_data = self.protecto_api.retry_failed_object(request_id)
                        
                        # Update session state
                        st.session_state['scan_data'] = updated_data
                        st.session_state['is_retry'] = True
                        
                        # Force refresh the page
                        st.rerun()

        except Exception as e:
            st.error(f"Error retrying scan: {str(e)}")
