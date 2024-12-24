import streamlit as st
import pandas as pd
from typing import Dict, List, Tuple
from protectoMethods import ProtectoAPI

class ScanPage:
    def __init__(self):
        self._init_session_state()
        self.protecto_api = ProtectoAPI()
        self.objects = self.protecto_api.get_list_of_objects()

    def _init_session_state(self):
        if 'view' not in st.session_state:
            st.session_state.view = None
        if 'scan_submitted' not in st.session_state:
            st.session_state.scan_submitted = False
        if 'submit_disabled' not in st.session_state:
            st.session_state.submit_disabled = True

    def show_start_scan(self):
        self._clear_state()
        st.session_state.view = 'start_scan'
        self._render_start_scan_view()

    def show_scan_progress(self):
        self._clear_state()
        st.session_state.view = 'scan_progress'
        self._render_scan_progress_view()

    def _clear_state(self):
        st.session_state.scan_submitted = False
        st.session_state.submit_disabled = True

    def _render_start_scan_view(self):
        if st.session_state.view == 'start_scan':
           
            
          st.title("Start scan")
          st.subheader("Select Object")
          selected_object = st.selectbox("", [""] + self.objects, key="object_select")
          
          if not selected_object:
              return
  
          try:
              fields = self.protecto_api.get_list_of_fields_for_object(selected_object)
              df, event = self._create_fields_table(fields)
              
              col1, col2 = st.columns(2)
              with col1:
                  if st.button("Save", use_container_width=True) and event:
                      self._handle_save(selected_object, df, event)
              
              with col2:
                  submit_button = st.button(
                      "Submit to scan",
                      use_container_width=True,
                      type="primary",
                      disabled=st.session_state.submit_disabled
                  )
                  
                  if submit_button:
                      self._handle_submit(df, event)
  
          except Exception as e:
              st.error(f"Error loading fields: {str(e)}")

    def _render_scan_progress_view(self):
        if st.session_state.view != 'scan_progress':
            return
            
        st.title("Scan Progress")
        try:
            progress_data = self.protecto_api.get_scan_progress()
            df = pd.DataFrame(progress_data)
            df['Progress'] = (df['scanned_count'] / df['total_count'] * 100).round(2)
            
            column_config = {
                "request_id": st.column_config.TextColumn("Request ID"),
                "object_name": st.column_config.TextColumn("Object"),
                "total_count": st.column_config.NumberColumn("Total Records"),
                "scanned_count": st.column_config.NumberColumn("Scanned Records"),
                "Progress": st.column_config.ProgressColumn("Progress (%)", min_value=0, max_value=100),
                "status": st.column_config.TextColumn("Status"),
                "last_updated_time": st.column_config.TextColumn("Last Updated"),
                "retry": "Retry"
            }
            
            edited_df = st.data_editor(
                df,
                column_config=column_config,
                disabled=["request_id", "object_name", "total_count", "scanned_count", 
                         "Progress", "status", "last_updated_time"],
                hide_index=True
            )

            self._handle_retries(edited_df)

        except Exception as e:
            st.error(f"Error displaying progress: {str(e)}")

    def _create_fields_table(self, fields_data: List[Dict]) -> Tuple[pd.DataFrame, st.delta_generator.DeltaGenerator]:
        df = pd.DataFrame(fields_data)
        if 'is_selected' not in df.columns:
            df['is_selected'] = False
        
        column_config = {
            "is_selected": st.column_config.CheckboxColumn("Selected", width="medium"),
            "field": st.column_config.TextColumn("Field", width="large"),
            "type": st.column_config.TextColumn("Type", width="large")
        }
        
        table = st.data_editor(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            key="fields_table"
        )
        return df, table

    def _handle_save(self, selected_object: str, df: pd.DataFrame, event: st.delta_generator.DeltaGenerator) -> None:
        # Get selected rows from the data_editor
        selected_rows = [i for i, row in df.iterrows() if row.get('is_selected', False)]
        
        if not selected_rows:
            st.warning("Please select fields to save")
            return

        filtered_df = df.iloc[selected_rows]
        selected_fields = filtered_df['field'].tolist()
        result = self.protecto_api.insert_or_update_scan_metadata(selected_object, selected_fields)
        
        if result.get('is_scan_submitted'):
            st.success(f"Saved {len(selected_fields)} fields successfully!")
            st.session_state.submit_disabled = False

    def _handle_submit(self, df: pd.DataFrame, event: st.delta_generator.DeltaGenerator) -> None:
        try:
            # Get selected rows from the data_editor
            selected_rows = [i for i, row in df.iterrows() if row.get('is_selected', False)]
            
            if not selected_rows:
                st.warning("Please select fields to scan")
                return

            filtered_df = df.iloc[selected_rows]
            selected_fields = filtered_df['field'].tolist()
            
            result = self.protecto_api.submit_to_scan(selected_fields)
            if result.get('is_scan_submitted'):
                st.success("Scan Complete!")
                st.session_state.scan_submitted = True
                st.session_state.submit_disabled = True
        except Exception as e:
            st.error(f"Error starting scan: {str(e)}")

    def _handle_retries(self, df: pd.DataFrame) -> None:
        for idx, row in df.iterrows():
            if row.get('retry'):
                if self.protecto_api.retry_failed_object(row['request_id']):
                    st.success("Retry initiated successfully!")
                    st.rerun()

if __name__ == "__main__":
    scan_page = ScanPage()
    #scan_page.show_start_scan()