import streamlit as st
import pandas as pd
from protectoMethods import ProtectoAPI

class ScanProgressView:
    def __init__(self, protecto_api: ProtectoAPI):
        self.protecto_api = protecto_api

    def render(self):
        st.title("Scan Progress")
        try:
            progress_data = self.protecto_api.get_scan_progress()
            df = pd.DataFrame(progress_data)
            #df['Progress'] = (df['scanned_count'] / df['total_count'] * 100).round(2)
            
            edited_df = self._create_progress_table(df)
            #self._handle_retries(edited_df)

        except Exception as e:
            st.error(f"Error displaying progress: {str(e)}")

    def _create_progress_table(self, df: pd.DataFrame) -> pd.DataFrame:
        column_config = {
            "request_id": st.column_config.TextColumn("Request ID"),
            "object_name": st.column_config.TextColumn("Object"),
            "total_count": st.column_config.NumberColumn("Total Records"),
            "scanned_count": st.column_config.NumberColumn("Scanned Records"),
            "status": st.column_config.TextColumn("Status"),
            "last_updated_time": st.column_config.TextColumn("Last Updated"),
            "retry": "Retry",
            "error": st.column_config.ButtonColumn("Error", help="Click to view error")
        }
        
        return st.data_editor(
            df,
            column_config=column_config,
            disabled=["request_id", "object_name", "total_count", "scanned_count", 
                     "Progress", "status", "last_updated_time"],
            hide_index=True
        )

   