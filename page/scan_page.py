import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple
from protectoMethods import ProtectoAPI

class ScanPage:
    def __init__(self):
        self.protecto_api = ProtectoAPI()
        self.objects = self.protecto_api.get_list_of_objects()

    def show_start_scan(self):
        st.title("Start scan")
        st.subheader("Select Object")
        
        selected_object = st.selectbox(
            "", 
            ["Select the Object Name"] + self.objects, 
            key="object_select"
        )
        
        if selected_object == "Select the Object Name":
            return
        
        st.markdown("""
                 <style>
                     [data-testid="stButton"] button {
                         width: 200px;  # Adjust this value as needed
                     }
                 </style>
                 """, unsafe_allow_html=True)

        try:
            fields = self.protecto_api.get_list_of_fields_for_object(selected_object)
            df, table = self._create_fields_table(fields)
            
            if st.button("Submit to scan", use_container_width=False, type="primary", key="submit_btn"):
               self._handle_submit(selected_object, df, table)

        except Exception as e:
            st.error(f"Error loading fields: {str(e)}")

    def _create_fields_table(self, fields_data: List[Dict]) -> Tuple[pd.DataFrame, st.delta_generator.DeltaGenerator]:
        df = pd.DataFrame(fields_data)
        if 'is_selected' not in df.columns:
            df['is_selected'] = False
        df = df[['is_selected', 'field']]    
    
        batch_size = 5
        total_pages = int(len(df) / batch_size) if int(len(df) / batch_size) > 0 else 1
        
        current_page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
        
        start_idx = (current_page - 1) * batch_size
        end_idx = start_idx + batch_size
        
        df_page = df.iloc[start_idx:end_idx].copy()
        
        column_config = {
            "is_selected": st.column_config.CheckboxColumn("Selected", width="medium"),
            "field": st.column_config.TextColumn("Field", width="large"),
        }
        
        editor = st.data_editor(
            df_page,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            key=f"fields_table_{current_page}"
        )
        
        df.iloc[start_idx:end_idx] = editor
        
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