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
            "to_be_masked": st.column_config.CheckboxColumn("To be masked?", width="small"),
            "field": st.column_config.TextColumn("Field", width="medium"),
            "pii_identified": st.column_config.ListColumn("PII Identified", width="medium"),
            "override_pii": st.column_config.SelectboxColumn(
                "Override PII",
                width="medium",
                options=["PERSON", "EMAIL", "NO PII", "URL", "ADDRESS", "PHONE"]
            ),
            "samples": st.column_config.ListColumn("Samples", width="large")
        }
        
        return st.data_editor(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
             column_order=["to_be_masked", "field", "pii_identified", "override_pii", "samples"]    
        )

    def show(self):
        st.title("Mask Configuration")
        
        # Object Selection
        st.subheader("Select Object")
        print("Select Object",self.objects)
        print("Select Object",st.session_state.selected_object)
        selected_object = st.selectbox(
             "Choose an object to configure masking",
             [""] + self.objects,
             key="mask_config_object",
             index=1 + self.objects.index(st.session_state.selected_object) 
         )
        
        
        if selected_object and selected_object != "":
            # Query Input
            st.subheader("Enter Query")
            query = st.text_area(
                "Enter WHERE clause",
                placeholder="e.g., case_date < '8/3/2015' AND geo='EU'",
                help="Enter the conditions to select records for masking",
                key="query_input"
            )
        
                
            try:
                # Get and display field metadata
                metadata = self.protecto_api.get_metadata_for_mask(st.session_state.selected_object)
                st.session_state.field_metadata = metadata.get('field_metadata', [])
                st.session_state.show_table = True
            except Exception as e:
                st.error(f"An error occurred while fetching metadata: {str(e)}")
                return
            
            # Show table only if Query button has been clicked
            # Create container for button at the top
            with st.container():
                schedule_button = st.button("Schedule for masking", type="primary", use_container_width=True)
            
            # Add spacing between button and table
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # Create container for table and its logic
            with st.container():
                # Create the table
                edited_fields = self._create_fields_table(st.session_state.field_metadata)
                
                # Handle button click after table is created
                if schedule_button:
                    try:
                        # Update mask metadata
                        result = self.protecto_api.update_mask_metadata(
                            selected_object,
                            query,
                            edited_fields.to_dict('records')
                        )
                        
                        if result.get('is_rows_selected_for_masking'):
                            st.success(result.get('message'))
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