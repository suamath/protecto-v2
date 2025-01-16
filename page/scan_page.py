import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple
from protectoMethods import ProtectoAPI

class ScanPage:
    def __init__(self):
        self.protecto_api = ProtectoAPI()
        self.objects = self.protecto_api.get_list_of_objects()

    def show_start_scan(self):
    # Initialize session states if not exists
        if 'submit_clicked' not in st.session_state:
            st.session_state.submit_clicked = False
        if 'submit_handled' not in st.session_state:
            st.session_state.submit_handled = False
    
        # Add custom CSS to reduce the top margin and spacing
        # Add this to your existing CSS styles:
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] {
                padding-top: 0;
            }
            .block-container {
                padding-top: 1.8rem;
                max-width: 100%;
            }
            .main-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: -3rem;
                padding: 0;
            }
            .main-title {
                margin: 0;
                padding: 0;
                font-size: 2rem;
                font-weight: bold;
            }
            
            /* Add these new styles */
            [data-testid="stSelectbox"] > label {
                height: 0px;
                padding-bottom: 0.5rem;
            }
            [data-testid="stTextInput"] > label {
                height: 0px;
                padding-bottom: 0.5rem;
            }
            div[data-testid="stSelectbox"], div[data-testid="stTextInput"] {
                padding-bottom: 0.5rem;
            }
            </style>
        """, unsafe_allow_html=True)
    
        # Header section with minimal spacing
        col1, col2 = st.columns([5, 1])
        with col1:
           st.title("Start scan")
        with col2:
            if st.button("🔄 Refresh", key="refresh_button"):
                st.session_state.submit_clicked = False
                st.session_state.submit_handled = False
                st.rerun()
    
        # Minimal spacing before Select Object
        
        if "selected_object" not in st.session_state:
            st.session_state.selected_object = "User"  
        
        # Selectbox with reduced spacing
        col1, col2 = st.columns([2, 2])
        with col1:
            selected_object = st.selectbox(
                "Object", 
                [""] + self.objects,
                key="mask_config_object",
                index=1 + self.objects.index(st.session_state.selected_object),
                on_change=lambda: st.session_state.update({"submit_clicked": False, "submit_handled": False})
            )
            st.session_state.selected_object = selected_object
        
        with col2:
            query = st.text_input(
                "Enter WHERE clause",
                placeholder="e.g., case_date < '8/3/2015' AND geo='EU'",
                help="Enter the conditions to select records for masking",
                key="query_input"
            )
            st.session_state.query = query
        
        if selected_object == "Select the Object Name":
            return
        
        try:
            fields = self.protecto_api.get_list_of_fields_for_object(selected_object)
            
            # Submit button
            submit_col1, submit_col2 = st.columns([4, 1])
            with submit_col2:
                submit_button = st.button(
                    "Submit to scan",
                    use_container_width=True,
                    type="primary",
                    key="submit_btn",
                    disabled=st.session_state.submit_clicked or not query.strip()  # Disable if empty
                )
            
            # Table
            df, table = self._create_fields_table(fields)
            
            if submit_button:
                if not query.strip():
                    st.error("Please enter a WHERE clause before submitting")
                    return
                st.session_state.submit_clicked = True
                st.rerun()
            
            if st.session_state.submit_clicked and not st.session_state.submit_handled:
                st.session_state.submit_handled = True
                self._handle_submit(selected_object, df, table)
        
        except Exception as e:
            st.error(f"Error loading fields: {str(e)}")

    def _create_fields_table(self, fields_data: List[Dict]) -> Tuple[pd.DataFrame, st.delta_generator.DeltaGenerator]:
        df = pd.DataFrame(fields_data)
        if 'is_selected' not in df.columns:
            df['is_selected'] = False
        df = df[['is_selected', 'field', 'type']]    

        # Initialize table page in session state if not exists
        if 'table_page' not in st.session_state:
            st.session_state.table_page = 1

        # Pagination settings
        batch_size = 7
        total_pages = max(1, (len(df) + batch_size - 1) // batch_size)

        # Ensure current page is within valid range
        st.session_state.table_page = min(max(1, st.session_state.table_page), total_pages)

        # Calculate indices
        start_idx = (st.session_state.table_page - 1) * batch_size
        end_idx = min(start_idx + batch_size, len(df))
        
        # Get current page's data
        df_page = df.iloc[start_idx:end_idx].copy()
        
        # Add table styling
        st.markdown("""
            <style>
            .stDataFrame {
                border: 1px solid #f0f2f6;
                border-radius: 0px;
                padding: -5 0;
                text-align: left !important;
            }
            .pagination-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.5rem;
                margin-top: 0.0rem;
                border-top: 1px solid #f0f2f6;
            }
            .page-info {
                color: #666;
                font-size: 0.9em;
            }
            </style>
        """, unsafe_allow_html=True)
        
        column_config = {
            "is_selected": st.column_config.CheckboxColumn("Select", width="small"),
            "field": st.column_config.TextColumn("Field", width="medium"),
            "type": st.column_config.TextColumn("Type", width="medium"),
        }
        
        # Create the data editor
        editor = st.data_editor(
            df_page,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            key=f"fields_table_{st.session_state.table_page}",
            height=400
        )
        
        # Update the main dataframe
        df.iloc[start_idx:end_idx] = editor
        
        # Create pagination controls below the table
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
            if cols[0].button("⬅️", disabled=st.session_state.table_page == 1, key="prev"):
                st.session_state.table_page -= 1
                st.rerun()
            
            # Page info
            cols[1].markdown(f"""
                <div style='text-align: center; color: #666;'>
                    Page {st.session_state.table_page} of {total_pages}
                </div>
            """, unsafe_allow_html=True)
            
            # Next button
            if cols[2].button("➡️", disabled=st.session_state.table_page == total_pages, key="next"):
                st.session_state.table_page += 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return df, editor

    def _handle_submit(self, selected_object: str, df: pd.DataFrame, event: st.delta_generator.DeltaGenerator) -> None:
        try:
            selected_rows = [i for i, row in df.iterrows() if row.get('is_selected', False)]
            
            if not selected_rows:
                st.warning("Please select fields to scan")
                return

            filtered_df = df.iloc[selected_rows]
            selected_fields = filtered_df['field'].tolist()
            
            save_result = self.protecto_api.insert_or_update_scan_metadata(selected_object, selected_fields)
            if save_result.get('is_scan_submitted'):
                st.success("Fields saved successfully!", icon="✅")
            
                scan_result = self.protecto_api.submit_to_scan(selected_fields)
                if scan_result.get('is_scan_submitted'):
                    st.success("Scan initiated successfully!", icon="✅")

        except Exception as e:
            st.error(f"Error in scan process: {str(e)}")