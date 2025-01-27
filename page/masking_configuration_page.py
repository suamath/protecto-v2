import streamlit as st
import pandas as pd
from protectoMethods import ProtectoAPI

class MaskConfigPage:
    def __init__(self):
        self.protecto_api = ProtectoAPI()
        self.objects = self.protecto_api.get_list_of_objects()
    
    def highlight_mask_status(self, df):
        colored = pd.DataFrame('', index=df.index, columns=df.columns)
        colored['field'] = df['to_be_masked'].apply(lambda x: 'background-color: #90EE90' if x == 'Yes' else 'background-color: #FFB6C6')
        return colored
        
    def _create_fields_table(self, fields_data):
        # Initialize the dataframe in session state if it doesn't exist
        if 'current_df' not in st.session_state:
            df = pd.DataFrame(fields_data)
            df['to_be_masked'] = df['to_be_masked'].map({True: 'Yes', False: 'No'})
            st.session_state.current_df = df
        
        column_config = {
            "to_be_masked": st.column_config.SelectboxColumn(
                "To be masked?",
                width="small",
                options=["Yes", "No"],
                help="Select Yes to mask this field, No to keep it as is",
                required=True
            ),
            "field": st.column_config.TextColumn("Field", width="medium"),
            "pii_identified": st.column_config.ListColumn("PII Identified", width="medium"),
            "override_pii": st.column_config.SelectboxColumn(
                "Override PII",
                width="medium",
                options=["PERSON", "EMAIL", "NO PII", "URL", "ADDRESS", "PHONE"]
            ),
            "samples": st.column_config.ListColumn("Samples", width="large")
        }
        
        # Apply styling to the current dataframe
        styled_df = st.session_state.current_df.style.apply(self.highlight_mask_status, axis=None)
         
        edited_df = st.data_editor(
            styled_df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            column_order=["field", "pii_identified", "override_pii", "to_be_masked", "samples"],
            disabled=["field"],
            key="data_editor"  # Add key to track changes
        )
         
        if edited_df is not None and not edited_df.equals(st.session_state.current_df):
            st.session_state.current_df = edited_df
            st.rerun()  # Force re-render when data changes
            
        if edited_df is not None:
            result_df = edited_df.copy()
            result_df['to_be_masked'] = result_df['to_be_masked'].map({'Yes': True, 'No': False})
            return result_df
        return None

    def show(self):
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] {
                padding-top: 0;
            }
            .block-container {
                padding-top: 1.0rem;
                max-width: 100%;
            }
            </style>
        """, unsafe_allow_html=True)
        st.title("Mask Configuration")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_object = st.selectbox(
                "Object",
                [""] + self.objects,
                key="mask_config_object",
                index=1 + self.objects.index(st.session_state.selected_object)
            )
            
        try:
            metadata = self.protecto_api.get_metadata_for_mask(st.session_state.selected_object)
            st.session_state.field_metadata = metadata.get('field_metadata', [])
            st.session_state.show_table = True
        except Exception as e:
            st.error(f"An error occurred while fetching metadata: {str(e)}")
            return
        
        with st.container():
            edited_fields = self._create_fields_table(st.session_state.field_metadata)
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col2:
                    schedule_button = st.button("Schedule for masking", type="primary")
            
            if schedule_button and edited_fields is not None:
                try:
                    fields_records = edited_fields.to_dict('records')
                    result = self.protecto_api.update_mask_metadata(
                        selected_object,
                        st.session_state.query,
                        fields_records
                    )
                    
                    if result.get('is_rows_selected_for_masking'):
                        st.success(result.get('message'))
                        st.session_state.show_table = False
                        if 'field_metadata' in st.session_state:
                            del st.session_state.field_metadata
                        if 'current_df' in st.session_state:
                            del st.session_state.current_df
                    else:
                        st.error("Failed to update mask configuration. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    mask_config_page = MaskConfigPage()
    mask_config_page.show()