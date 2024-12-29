import streamlit as st
import pandas as pd
from protectoMethods import ProtectoAPI

class MaskConfigPage:
    def __init__(self):
        self.protecto_api = ProtectoAPI()
        self.objects = self.protecto_api.get_list_of_objects()
        
    def _create_fields_table(self, fields_data):
        df = pd.DataFrame(fields_data)
        column_config = {
            "field": st.column_config.TextColumn("Field", width="medium"),
            "pii_identified": st.column_config.ListColumn("PII Identified", width="medium"),
            "override_pii": st.column_config.SelectboxColumn(
                "Override PII",
                width="medium",
                options=["PERSON", "EMAIL", "NO PII", "URL", "ADDRESS", "PHONE"]
            ),
            "to_be_masked": st.column_config.CheckboxColumn("To be masked?", width="small"),
            "samples": st.column_config.ListColumn("Samples", width="large")
        }
        
        return st.data_editor(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed"
        )

    def show(self):
        st.title("Mask Configuration")
        
        # Object Selection
        st.subheader("Select Object")
        selected_object = st.selectbox(
            "Choose an object to configure masking",
            [""] + self.objects,
            key="mask_config_object"
        )
        
        if selected_object and selected_object != "":
            # Query Input
            st.subheader("Enter Query")
            query = st.text_area(
                "Enter WHERE clause for data selection",
                placeholder="e.g., case_date < '8/3/2015' AND geo='EU'",
                help="Enter the conditions to select records for masking",
                key="query_input"
            )
            
            # Query button
            # if st.button("Query", type="primary", use_container_width=True):
            #     if not query:
            #         st.error("Please enter a query before proceeding.")
            #         return
                
            try:
                # Get and display field metadata
                metadata = self.protecto_api.get_metadata_for_mask(st.session_state.selected_object)
                st.session_state.field_metadata = metadata.get('field_metadata', [])
                st.session_state.show_table = True
            except Exception as e:
                st.error(f"An error occurred while fetching metadata: {str(e)}")
                return
            
            # Show table only if Query button has been clicked
            #if st.session_state.get('show_table', False):
            st.subheader("Configure Fields")
            edited_fields = self._create_fields_table(st.session_state.field_metadata)
            
            # Update Configuration button
            if st.button("Update Mask Configuration", type="primary", use_container_width=True):
                try:
                    # Update mask metadata
                    result = self.protecto_api.get_metadata_for_mask(
                        selected_object,
                        query,
                        edited_fields.to_dict('records')
                    )
                    
                    if result.get('is_rows_selected_for_masking'):
                        st.success(result.get('message', 'Mask configuration updated successfully!'))
                        # Clear the session state to refresh the data
                        st.session_state.show_table = False
                        if 'field_metadata' in st.session_state:
                            del st.session_state.field_metadata
                    else:
                        st.error("Failed to update mask configuration. Please try again.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    mask_config_page = MaskConfigPage()
    mask_config_page.show()